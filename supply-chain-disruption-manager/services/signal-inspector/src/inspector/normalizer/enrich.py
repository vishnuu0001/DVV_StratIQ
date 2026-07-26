# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Stage 3: Enrichment — resolve root_node_id from KG service.
# Date: 2026-03-01
# ---------------------------------------------------------------------------
"""Stage 3: Enrichment — resolve root_node_id from KG service."""

from __future__ import annotations

from typing import Any

import httpx
import structlog

from inspector.config import get_settings

logger = structlog.get_logger(__name__)

# Ordered list of (payload_key, kg_entity_type) lookups
_ENTITY_LOOKUPS: list[tuple[str, str]] = [
    ("supplier_id", "Supplier"),
    ("po_id", "PurchaseOrder"),
    ("shipment_id", "Shipment"),
    ("warehouse_id", "Warehouse"),
    ("workcenter_id", "WorkCenter"),
    ("product_id", "Product"),
    ("grn_id", "GoodsReceiptNote"),
    ("customer_id", "Customer"),
    ("order_id", "SalesOrder"),
]


# Function: enrich_payload
async def enrich_payload(
    payload: dict[str, Any],
    http_client: httpx.AsyncClient,
) -> tuple[str | None, dict[str, Any]]:
    """Look up root_node_id from KG service.

    Tries each entity lookup in order. Returns (root_node_id, updated_payload).
    On any HTTP error, returns (None, payload) and continues without enrichment.
    """
    settings = get_settings()
    headers = {"X-API-Key": settings.kg_api_key}

    for payload_key, entity_type in _ENTITY_LOOKUPS:
        entity_id = payload.get(payload_key)
        if not entity_id:
            continue

        url = f"{settings.kg_base_url}/entity/{entity_type}/{entity_id}"
        try:
            resp = await http_client.get(url, headers=headers, timeout=5.0)
            if resp.status_code == 200:
                data = resp.json()
                node_id = data.get("node_id") or data.get("id")
                if node_id:
                    logger.debug(
                        "enrich.resolved",
                        payload_key=payload_key,
                        entity_type=entity_type,
                        entity_id=entity_id,
                        node_id=node_id,
                    )
                    return str(node_id), payload
            elif resp.status_code == 404:
                logger.debug(
                    "enrich.not_found",
                    payload_key=payload_key,
                    entity_type=entity_type,
                    entity_id=entity_id,
                )
            else:
                logger.warning(
                    "enrich.unexpected_status",
                    url=url,
                    status=resp.status_code,
                )
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "enrich.error",
                url=url,
                error=str(exc),
            )

    return None, payload
