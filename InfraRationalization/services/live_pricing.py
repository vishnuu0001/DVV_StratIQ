# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: services/live_pricing.py
# Date: 2025-08-10
# ---------------------------------------------------------------------------
"""
services/live_pricing.py
Live multi-cloud VM pricing (AWS / Azure / GCP / OCI) from each provider's
public list-price APIs, replacing the static "approximate 2025" tables that
were the only pricing source before this module existed.

Design constraints, all deliberate:
  - Every fetch function degrades to returning {} on ANY failure (network
    unreachable, API shape change, timeout, missing API key) rather than
    raising. This module explicitly supports air-gapped / regulated customer
    environments (see README), where outbound internet access to these
    pricing APIs may not exist at all — callers MUST keep working from the
    static catalogs in scanner/cloud_pricing.py and services/tco_rightsizing.py
    when live data isn't available. Live pricing is a freshness upgrade,
    never a hard dependency.
  - Results are cached to disk with a TTL (default 24h) so a normal, connected
    deployment doesn't re-fetch multi-hundred-KB catalogs on every TCO
    request, and so the module is still fast on a connected-but-slow link.
  - AWS and OCI pricing APIs are fully public (no account/credentials needed).
    Azure's Retail Prices API is also public/unauthenticated. GCP's Cloud
    Billing Catalog API is the one exception — it requires an API key even
    for public list prices; if GOOGLE_CLOUD_API_KEY isn't set, GCP live
    pricing is simply skipped (static table is used), which is expected and
    not an error condition.
"""
from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Optional

import requests

log = logging.getLogger(__name__)

_CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "pricing_cache"
_CACHE_TTL_SECONDS = 24 * 60 * 60   # 24h — list prices don't change intra-day
_REQUEST_TIMEOUT = 12               # seconds — never let a slow pricing API stall a scan/TCO request

_AZURE_RETAIL_PRICES_URL = "https://prices.azure.com/api/retail/prices"
_AWS_PRICING_INDEX_URL = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/region_index.json"
_GCP_BILLING_CATALOG_URL = "https://cloudbilling.googleapis.com/v1/services/6F81-5844-456A/skus"  # Compute Engine service id
_OCI_PRICING_URL = "https://apexapps.oracle.com/pls/apex/cetools/api/v1/products/"


# Function: _cache_path
def _cache_path(provider: str, region: str) -> Path:
    return _CACHE_DIR / f"{provider}_{region}.json"


# Function: _read_cache
def _read_cache(provider: str, region: str) -> Optional[dict]:
    path = _cache_path(provider, region)
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if time.time() - payload.get("fetched_at", 0) > _CACHE_TTL_SECONDS:
            return None
        return payload
    except Exception:
        return None


# Function: _write_cache
def _write_cache(provider: str, region: str, prices: dict[str, float]) -> None:
    try:
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        _cache_path(provider, region).write_text(
            json.dumps({"fetched_at": time.time(), "region": region, "prices": prices}),
            encoding="utf-8",
        )
    except Exception as exc:
        log.debug("live_pricing: failed to write cache for %s/%s: %s", provider, region, exc)


# Function: _cache_age_label
def _cache_age_label(fetched_at: float) -> str:
    age_h = (time.time() - fetched_at) / 3600
    if age_h < 1:
        return "just now"
    if age_h < 24:
        return f"{int(age_h)}h ago"
    return f"{int(age_h / 24)}d ago"


# ─── AWS EC2 (public, no credentials required) ────────────────────────────────

# Function: fetch_aws_prices
def fetch_aws_prices(region: str = "us-east-1", instance_types: Optional[list[str]] = None) -> dict[str, Any]:
    """
    Returns {"source": "live"|"cache"|"unavailable", "fetched_at": ts|None,
             "prices": {instance_type: on_demand_linux_usd_hourly}}
    AWS's Price List Bulk API is a plain, unauthenticated HTTPS JSON endpoint —
    no AWS account or API key needed, unlike the boto3 `pricing` client.
    """
    cached = _read_cache("aws", region)
    if cached:
        return {"source": "cache", "fetched_at": cached["fetched_at"],
                 "cache_age": _cache_age_label(cached["fetched_at"]), "prices": cached["prices"]}

    try:
        idx = requests.get(_AWS_PRICING_INDEX_URL, timeout=_REQUEST_TIMEOUT).json()
        region_entry = idx.get("regions", {}).get(region)
        if not region_entry:
            return {"source": "unavailable", "fetched_at": None, "prices": {}}
        offer_url = "https://pricing.us-east-1.amazonaws.com" + region_entry["currentVersionUrl"]
        offer = requests.get(offer_url, timeout=_REQUEST_TIMEOUT).json()

        prices: dict[str, float] = {}
        products = offer.get("products", {})
        terms = offer.get("terms", {}).get("OnDemand", {})
        wanted = set(instance_types) if instance_types else None

        for sku, product in products.items():
            attrs = product.get("attributes", {})
            if attrs.get("operatingSystem") != "Linux":
                continue
            if attrs.get("tenancy") != "Shared":
                continue
            if attrs.get("preInstalledSw", "NA") != "NA":
                continue
            itype = attrs.get("instanceType")
            if not itype or (wanted and itype not in wanted):
                continue
            sku_terms = terms.get(sku, {})
            for term in sku_terms.values():
                for dim in term.get("priceDimensions", {}).values():
                    usd = dim.get("pricePerUnit", {}).get("USD")
                    if usd:
                        prices[itype] = round(float(usd), 4)
                        break

        if not prices:
            return {"source": "unavailable", "fetched_at": None, "prices": {}}
        _write_cache("aws", region, prices)
        return {"source": "live", "fetched_at": time.time(), "cache_age": "just now", "prices": prices}
    except Exception as exc:
        log.info("live_pricing: AWS fetch failed (falling back to static table): %s", exc)
        return {"source": "unavailable", "fetched_at": None, "prices": {}}


# ─── Azure Retail Prices API (public, no credentials required) ───────────────

# Function: fetch_azure_prices
def fetch_azure_prices(region: str = "eastus", vm_names: Optional[list[str]] = None) -> dict[str, Any]:
    """
    Returns the same shape as fetch_aws_prices. Azure's Retail Prices API
    supports OData filtering server-side, so we can request only Linux,
    Consumption (PAYG), Virtual Machines in one region directly.
    """
    cached = _read_cache("azure", region)
    if cached:
        return {"source": "cache", "fetched_at": cached["fetched_at"],
                 "cache_age": _cache_age_label(cached["fetched_at"]), "prices": cached["prices"]}

    try:
        odata_filter = (
            f"armRegionName eq '{region}' and priceType eq 'Consumption' "
            f"and serviceName eq 'Virtual Machines'"
        )
        prices: dict[str, float] = {}
        url = _AZURE_RETAIL_PRICES_URL
        params = {"$filter": odata_filter, "currencyCode": "USD"}
        wanted = {v.lower() for v in vm_names} if vm_names else None
        pages_fetched = 0

        while url and pages_fetched < 20:   # hard cap — Azure's catalog is large; 20 pages is generous
            resp = requests.get(url, params=params if pages_fetched == 0 else None, timeout=_REQUEST_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            for item in data.get("Items", []):
                if item.get("productName", "").endswith("Windows"):
                    continue   # Linux base pricing only — matches the static catalog's convention
                sku = item.get("armSkuName") or item.get("skuName")
                if not sku:
                    continue
                if wanted and sku.lower() not in wanted:
                    continue
                price = item.get("retailPrice")
                if price:
                    # Azure returns hourly retail price
                    prices[sku] = round(float(price), 4)
            url = data.get("NextPageLink")
            pages_fetched += 1

        if not prices:
            return {"source": "unavailable", "fetched_at": None, "prices": {}}
        _write_cache("azure", region, prices)
        return {"source": "live", "fetched_at": time.time(), "cache_age": "just now", "prices": prices}
    except Exception as exc:
        log.info("live_pricing: Azure fetch failed (falling back to static table): %s", exc)
        return {"source": "unavailable", "fetched_at": None, "prices": {}}


# ─── GCP Cloud Billing Catalog API (public data, but requires an API key) ─────

# Function: fetch_gcp_prices
def fetch_gcp_prices(region: str = "us-central1", machine_types: Optional[list[str]] = None) -> dict[str, Any]:
    """
    Same return shape. Unlike AWS/Azure, GCP's Cloud Billing Catalog API
    requires an API key even though the data itself (list prices) is public —
    Google gates the endpoint, not the data. Without GOOGLE_CLOUD_API_KEY set,
    this is a normal, expected no-op (not an error): the static GCP catalog is
    used instead.
    """
    api_key = os.getenv("GOOGLE_CLOUD_API_KEY", "").strip()
    if not api_key:
        log.debug("live_pricing: GOOGLE_CLOUD_API_KEY not set — using static GCP catalog")
        return {"source": "unavailable", "fetched_at": None, "prices": {}}

    cached = _read_cache("gcp", region)
    if cached:
        return {"source": "cache", "fetched_at": cached["fetched_at"],
                 "cache_age": _cache_age_label(cached["fetched_at"]), "prices": cached["prices"]}

    try:
        prices: dict[str, float] = {}
        page_token = None
        pages_fetched = 0
        wanted = set(machine_types) if machine_types else None

        while pages_fetched < 20:
            params: dict[str, Any] = {"key": api_key, "pageSize": 5000}
            if page_token:
                params["pageToken"] = page_token
            resp = requests.get(_GCP_BILLING_CATALOG_URL, params=params, timeout=_REQUEST_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            for sku in data.get("skus", []):
                desc = sku.get("description", "")
                if "Running" not in desc or "Custom" in desc:
                    continue
                geo = sku.get("serviceRegions", [])
                if region not in geo and "global" not in [g.lower() for g in geo]:
                    continue
                machine_type = _gcp_machine_type_from_sku(sku)
                if not machine_type or (wanted and machine_type not in wanted):
                    continue
                pricing_info = sku.get("pricingInfo", [{}])[0]
                units = pricing_info.get("pricingExpression", {}).get("tieredRates", [])
                if units:
                    unit_price = units[-1].get("unitPrice", {})
                    nanos = unit_price.get("nanos", 0)
                    usd = unit_price.get("units", "0")
                    hourly = float(usd) + nanos / 1e9
                    if hourly:
                        prices[machine_type] = round(hourly, 4)
            page_token = data.get("nextPageToken")
            pages_fetched += 1
            if not page_token:
                break

        if not prices:
            return {"source": "unavailable", "fetched_at": None, "prices": {}}
        _write_cache("gcp", region, prices)
        return {"source": "live", "fetched_at": time.time(), "cache_age": "just now", "prices": prices}
    except Exception as exc:
        log.info("live_pricing: GCP fetch failed (falling back to static table): %s", exc)
        return {"source": "unavailable", "fetched_at": None, "prices": {}}


# Function: _gcp_machine_type_from_sku
def _gcp_machine_type_from_sku(sku: dict) -> Optional[str]:
    category = sku.get("category", {})
    resource_group = category.get("resourceGroup", "")
    desc = sku.get("description", "")
    # SKU descriptions look like "N2 Instance Core running in Americas" — this
    # is a best-effort mapping, not exhaustive; unresolved SKUs are skipped
    # rather than guessed at, since a wrong price is worse than no live price.
    for family in ("E2", "N2", "N2D", "C2", "M1"):
        if desc.startswith(family):
            return resource_group or None
    return None


# ─── Oracle Cloud Infrastructure (public, no credentials required) ───────────

# Function: fetch_oci_prices
def fetch_oci_prices(region: str = "us-ashburn-1") -> dict[str, Any]:
    """
    OCI publishes a fully public pricing catalog (no auth). It's not
    region-specific in the same way AWS/Azure are (OCI list prices are
    largely uniform across commercial regions), so *region* is accepted for
    interface symmetry and cache-keying but doesn't change the query.

    Unlike AWS/Azure/GCP, OCI's "Compute - Virtual Machine" category bills
    flexible shapes per-OCPU and per-GB-memory SEPARATELY rather than one
    flat hourly rate per named instance type (confirmed against the live
    catalog: e.g. "Standard - A2" has one line-item priced per OCPU/hour and
    a second priced per GB-memory/hour). Forcing this into the same
    {instance_name: flat_hourly_price} shape the other three providers use
    would silently misrepresent OCI's actual billing model, so this returns
    {"shapes": {family: {"ocpu_hourly": x, "mem_gb_hourly": y}}} instead —
    callers compute total_hourly = ocpu_hourly * cpu_cores + mem_gb_hourly * ram_gb,
    which is exactly how OCI's own pricing calculator works for flexible shapes.
    """
    cached = _read_cache("oci", region)
    if cached:
        return {"source": "cache", "fetched_at": cached["fetched_at"],
                 "cache_age": _cache_age_label(cached["fetched_at"]), "shapes": cached["prices"]}

    try:
        resp = requests.get(_OCI_PRICING_URL, timeout=_REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        shapes: dict[str, dict[str, float]] = {}

        for item in data.get("items", []):
            if item.get("serviceCategory") != "Compute - Virtual Machine":
                continue
            display_name = item.get("displayName", "")
            metric = item.get("metricName", "")
            usd_entry = next(
                (c for c in item.get("currencyCodeLocalizations", []) if c.get("currencyCode") == "USD"),
                None,
            )
            payg = next(
                (p for p in (usd_entry or {}).get("prices", []) if p.get("model") == "PAY_AS_YOU_GO"),
                None,
            )
            if not payg or not payg.get("value"):
                continue
            value = round(float(payg["value"]), 4)

            # Family name = display name with the trailing " OCPU"/" Memory" stripped.
            family = display_name.replace(" OCPU", "").replace(" Memory", "").strip().rstrip(" -").strip()
            shapes.setdefault(family, {})
            if "OCPU" in metric:
                shapes[family]["ocpu_hourly"] = value
            elif "Gigabyte" in metric or "GB" in metric:
                shapes[family]["mem_gb_hourly"] = value

        # Only keep shapes where we resolved BOTH components — a partial shape
        # (e.g. OCPU rate found but memory rate missing) can't produce a valid
        # total and would silently understate cost if used as-is.
        shapes = {k: v for k, v in shapes.items() if "ocpu_hourly" in v and "mem_gb_hourly" in v}

        if not shapes:
            return {"source": "unavailable", "fetched_at": None, "shapes": {}}
        _write_cache("oci", region, shapes)
        return {"source": "live", "fetched_at": time.time(), "cache_age": "just now", "shapes": shapes}
    except Exception as exc:
        log.info("live_pricing: OCI fetch failed (falling back to static table): %s", exc)
        return {"source": "unavailable", "fetched_at": None, "shapes": {}}


# Function: oci_hourly_cost
def oci_hourly_cost(shapes: dict[str, dict[str, float]], family: str, cpu_cores: int, ram_gb: float) -> Optional[float]:
    """Compute total hourly cost for *cpu_cores*/*ram_gb* on a given OCI flexible shape family."""
    rates = shapes.get(family)
    if not rates:
        return None
    return round(rates["ocpu_hourly"] * cpu_cores + rates["mem_gb_hourly"] * ram_gb, 4)


# ─── Unified status (for the frontend's pricing-freshness indicator) ─────────

# Function: get_pricing_freshness
def get_pricing_freshness() -> dict[str, Any]:
    """
    Report per-provider pricing source/freshness without triggering a new
    fetch — reads only whatever is already cached on disk. Used by the
    frontend to show a 'Pricing: live (2h ago)' / 'Pricing: static table'
    badge so TCO figures are never presented without their real provenance.
    """
    out: dict[str, Any] = {}
    for provider, region in (
        ("aws", "us-east-1"), ("azure", "eastus"), ("gcp", "us-central1"), ("oci", "us-ashburn-1"),
    ):
        cached = _read_cache(provider, region)
        if cached:
            out[provider] = {
                "source": "live", "region": region,
                "fetched_at": cached["fetched_at"], "cache_age": _cache_age_label(cached["fetched_at"]),
            }
        else:
            out[provider] = {"source": "static", "region": region, "fetched_at": None, "cache_age": None}
    return out


# Function: refresh_all
def refresh_all(regions: Optional[dict[str, str]] = None) -> dict[str, Any]:
    """
    Force-refresh live pricing for all four providers (ignoring cache TTL).
    Returns a summary of what succeeded/fell back — callers use this to
    surface a clear "3 of 4 providers refreshed live, GCP fell back to
    static (no API key configured)" style message rather than silent partial success.
    """
    regions = regions or {}
    # Bypass the cache read for this explicit refresh by clearing any fresh entry first.
    for provider, region in (
        ("aws", regions.get("aws", "us-east-1")),
        ("azure", regions.get("azure", "eastus")),
        ("gcp", regions.get("gcp", "us-central1")),
        ("oci", regions.get("oci", "us-ashburn-1")),
    ):
        try:
            _cache_path(provider, region).unlink(missing_ok=True)
        except Exception:
            pass

    results = {
        "aws": fetch_aws_prices(regions.get("aws", "us-east-1")),
        "azure": fetch_azure_prices(regions.get("azure", "eastus")),
        "gcp": fetch_gcp_prices(regions.get("gcp", "us-central1")),
        "oci": fetch_oci_prices(regions.get("oci", "us-ashburn-1")),
    }
    return {
        provider: {"source": r["source"], "vm_count": len(r["prices"])}
        for provider, r in results.items()
    }
