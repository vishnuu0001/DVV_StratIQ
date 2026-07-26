# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: scanner/pdf_scanner.py
# Date: 2026-02-17
# ---------------------------------------------------------------------------
"""
scanner/pdf_scanner.py
Deep OCR-based infrastructure document scanner.

Processes PDF documents (architecture diagrams, feasibility studies, server
inventories, migration assessments) from the data/ directory using:
  1. pdfplumber  — native text extraction (vector PDFs — highest accuracy)
  2. pdf2image + pytesseract — OCR fallback for scanned / image-only pages

Provider Detection:
  - Detects: On-Premises, Azure, AWS, GCP (or mixed/hybrid)
  - Extracts all infrastructure features, services, components, and specs
    mentioned in the document

Extracted information per provider:
  On-Premises : server specs (CPU/RAM/disk), OS, network topology, workloads,
                storage tiers, virtualisation, DR/HA, VLAN/subnet details
  Azure       : Subscription/RG/region, VM SKUs, VNet/NSG/ASG, Azure services
                (AKS, Azure SQL, Cosmos DB, Storage Account, App Service,
                Azure AD, Key Vault, Monitor, Defender …)
  AWS         : Account/region, EC2 instance types, VPC/subnets/SG, AWS services
                (EKS, RDS, S3, CloudFront, IAM, KMS, CloudWatch, WAF …)
  GCP         : Project/region/zone, Compute Engine SKUs, GKE, Cloud SQL,
                GCS, Cloud IAM, VPC/Firewall rules, Cloud Monitoring …

All extracted features are mapped to DiscoveredServer objects AND returned in
a rich `pdf_features` dict attached to the scan report for full traceability.
"""
from __future__ import annotations

import io
import logging
import os
import re
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .models import (
    DiscoveredServer,
    DiskInfo,
    NetworkInterface,
    ScanTarget,
    WorkloadComponent,
)

log = logging.getLogger(__name__)

# ── regex helpers ─────────────────────────────────────────────────────────────

_RE_IP     = re.compile(r'\b(\d{1,3}(?:\.\d{1,3}){3})\b')
_RE_CIDR   = re.compile(r'\b(\d{1,3}(?:\.\d{1,3}){3}/\d{1,2})\b')
_RE_CPU    = re.compile(r'(\d+)\s*(?:x\s*)?(?:v?cpu|core|processor)', re.IGNORECASE)
_RE_RAM    = re.compile(r'(\d+(?:\.\d+)?)\s*(?:GB|GiB)\s*(?:RAM|Memory|DRAM)', re.IGNORECASE)
_RE_DISK   = re.compile(r'(\d+(?:\.\d+)?)\s*(?:GB|GiB|TB|TiB)\s*(?:Storage|Disk|SSD|HDD|NVMe)', re.IGNORECASE)
_RE_HOSTNAME = re.compile(r'(?:Hostname|Server Name|Host)\s*[:\-=]\s*([A-Za-z0-9_\-\.]+)', re.IGNORECASE)
_RE_OS     = re.compile(
    r'(Windows Server\s*\d{4}|Ubuntu\s*\d{2}\.\d{2}|Red Hat Enterprise Linux\s*\d|'
    r'CentOS\s*\d|Debian\s*\d+|SUSE\s*\d+|Oracle Linux\s*\d)', re.IGNORECASE)
_RE_ENV    = re.compile(r'(?:Environment|Env)\s*[:\-=]\s*(Production|Development|Test|Staging|DR)', re.IGNORECASE)
_RE_REGION = re.compile(
    r'\b(East US|West US|Central US|North Europe|West Europe|Southeast Asia|'
    r'East Asia|UK South|UK West|Australia East|'
    r'us-east-\d|us-west-\d|eu-west-\d|ap-southeast-\d|'
    r'us-central1|europe-west\d|asia-east\d)\b', re.IGNORECASE)

# ── Provider keyword dictionaries ─────────────────────────────────────────────

_AZURE_SERVICES = [
    # Compute
    "Azure Virtual Machine", "VM Scale Set", "VMSS", "Azure Kubernetes Service",
    "AKS", "App Service", "Azure Functions", "Container Instances", "ACI",
    "Azure Batch",
    # Networking
    "Virtual Network", "VNet", "Network Security Group", "NSG",
    "Application Security Group", "ASG", "Azure Load Balancer", "Application Gateway",
    "Azure Firewall", "VPN Gateway", "ExpressRoute", "Traffic Manager",
    "Azure CDN", "Azure DNS", "Private Endpoint", "Private Link",
    "Azure Bastion", "Route Table", "Subnet",
    # Storage
    "Azure Storage Account", "Blob Storage", "Azure Files", "Azure Disk",
    "Managed Disk", "Azure Data Lake",
    # Database
    "Azure SQL", "SQL Managed Instance", "Azure Database for MySQL",
    "Azure Database for PostgreSQL", "Cosmos DB", "Azure Cache for Redis",
    "Azure Synapse", "Azure Data Factory",
    # Identity & Security
    "Azure Active Directory", "Azure AD", "Entra ID", "Key Vault",
    "Microsoft Defender for Cloud", "Defender for Servers",
    "Microsoft Sentinel", "Azure Policy", "RBAC", "Managed Identity",
    # Monitoring
    "Azure Monitor", "Log Analytics", "Application Insights",
    "Azure Alerts", "Diagnostic Settings",
    # Governance
    "Azure Resource Group", "Management Group", "Azure Subscription",
    "Azure Blueprint", "Cost Management",
    # Migration
    "Azure Migrate", "Azure Site Recovery", "ASR",
]

_AWS_SERVICES = [
    # Compute
    "EC2", "Amazon EC2", "Auto Scaling Group", "ASG", "Lambda",
    "Elastic Kubernetes Service", "EKS", "Elastic Container Service", "ECS",
    "AWS Fargate", "Elastic Beanstalk",
    # Networking
    "VPC", "Amazon VPC", "Subnet", "Security Group", "Route Table",
    "Internet Gateway", "NAT Gateway", "Elastic Load Balancer", "ELB",
    "Application Load Balancer", "ALB", "Network Load Balancer", "NLB",
    "CloudFront", "Route 53", "AWS Direct Connect", "VPN",
    "VPC Peering", "Transit Gateway",
    # Storage
    "S3", "Amazon S3", "EBS", "Elastic Block Store", "EFS",
    "Amazon Glacier", "FSx",
    # Database
    "RDS", "Amazon RDS", "Aurora", "DynamoDB", "Redshift",
    "ElastiCache", "Amazon Neptune", "DocumentDB",
    # Identity & Security
    "IAM", "AWS IAM", "KMS", "AWS KMS", "AWS WAF", "AWS Shield",
    "Amazon GuardDuty", "AWS Secrets Manager", "AWS Certificate Manager",
    "AWS Config", "CloudTrail",
    # Monitoring
    "CloudWatch", "Amazon CloudWatch", "AWS X-Ray", "AWS Cost Explorer",
    # Migration
    "AWS Migration Hub", "AWS DMS", "Server Migration Service",
    # Messaging
    "SQS", "SNS", "Amazon SQS", "Amazon SNS", "Amazon MQ",
]

_GCP_SERVICES = [
    # Compute
    "Compute Engine", "GCE", "Google Kubernetes Engine", "GKE",
    "Cloud Run", "App Engine", "Cloud Functions",
    # Networking
    "VPC", "Google VPC", "Cloud VPN", "Cloud Interconnect", "Cloud NAT",
    "Cloud Load Balancing", "Cloud CDN", "Cloud DNS", "Firewall Rules",
    "VPC Peering", "Private Google Access",
    # Storage
    "Cloud Storage", "GCS", "Persistent Disk", "Filestore",
    # Database
    "Cloud SQL", "Cloud Spanner", "Firestore", "Bigtable",
    "Memorystore", "BigQuery",
    # Identity & Security
    "Cloud IAM", "Google IAM", "Cloud KMS", "Cloud Armor",
    "Security Command Center", "Secret Manager",
    # Monitoring
    "Cloud Monitoring", "Cloud Logging", "Cloud Trace",
    # Migration
    "Migrate for Compute Engine", "Database Migration Service",
    # Messaging
    "Pub/Sub", "Cloud Tasks",
]

_ONPREM_FEATURES = [
    # Virtualisation
    "VMware vSphere", "VMware ESXi", "vSAN", "vCenter", "NSX",
    "Hyper-V", "KVM", "Xen", "RHEV", "oVirt",
    # Storage
    "SAN", "NAS", "iSCSI", "FC SAN", "NFS", "SMB", "CIFS",
    "NetApp", "EMC", "Pure Storage", "HPE Nimble", "3PAR",
    # Networking
    "Cisco", "Juniper", "Arista", "F5", "VLAN", "BGP", "OSPF",
    "MPLS", "SDN",
    # Directory / Auth
    "Active Directory", "LDAP", "RADIUS", "PKI", "Certificate Authority",
    # Security
    "Firewall", "IDS", "IPS", "SIEM", "PAM", "Bastion Host",
    # HA/DR
    "Load Balancer", "Failover Cluster", "DR Site", "RPO", "RTO",
    "Disaster Recovery", "High Availability",
    # Monitoring
    "SCOM", "Nagios", "Zabbix", "Prometheus", "SNMP",
    # Bare-metal features
    "Physical Server", "Blade Server", "Rack Server",
    "IPMI", "iDRAC", "iLO", "BIOS", "UEFI",
]


# ── PDF text extraction ───────────────────────────────────────────────────────

# Function: _extract_text_pdfplumber
def _extract_text_pdfplumber(pdf_path: Path) -> list[str]:
    """Extract per-page text using pdfplumber (native vector text)."""
    try:
        import pdfplumber
        pages = []
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                # Also extract table cell values
                for table in (page.extract_tables() or []):
                    for row in table:
                        if row:
                            text += " " + " ".join(str(c) for c in row if c)
                pages.append(text)
        return pages
    except ImportError:
        log.warning("pdfplumber not installed — skipping native text extraction")
        return []
    except Exception as exc:
        log.warning("pdfplumber failed for %s: %s", pdf_path.name, exc)
        return []


# Function: _extract_text_ocr
def _extract_text_ocr(pdf_path: Path) -> list[str]:
    """OCR fallback using pdf2image + pytesseract for image/scanned PDFs."""
    try:
        from pdf2image import convert_from_path
        import pytesseract
        pages = []
        images = convert_from_path(str(pdf_path), dpi=300)
        for img in images:
            text = pytesseract.image_to_string(img, config="--psm 3")
            pages.append(text)
        return pages
    except ImportError as ie:
        log.warning("OCR deps not installed (%s) — skipping OCR pass", ie)
        return []
    except Exception as exc:
        log.warning("OCR failed for %s: %s", pdf_path.name, exc)
        return []


# Function: _extract_all_text
def _extract_all_text(pdf_path: Path) -> tuple[list[str], str]:
    """
    Try pdfplumber first (fast, accurate).
    Fall back to OCR if pages have < 50 chars of extractable text (scanned PDF).
    Returns (pages: list[str], method: str).
    """
    pages = _extract_text_pdfplumber(pdf_path)
    total_chars = sum(len(p) for p in pages)

    if total_chars < 200:
        log.info("%s appears to be a scanned PDF — running OCR", pdf_path.name)
        ocr_pages = _extract_text_ocr(pdf_path)
        if ocr_pages:
            return ocr_pages, "ocr"
        # If OCR also fails, return what pdfplumber gave us
        return pages, "pdfplumber_fallback"

    return pages, "pdfplumber"


# ── Provider detection ────────────────────────────────────────────────────────

# Function: _detect_providers
def _detect_providers(full_text: str) -> list[str]:
    """
    Return list of detected providers: 'onprem', 'azure', 'aws', 'gcp'.
    A document can mention multiple providers (hybrid/multi-cloud).
    """
    providers = []
    lower = full_text.lower()

    azure_hits = sum(1 for kw in _AZURE_SERVICES if kw.lower() in lower)
    aws_hits   = sum(1 for kw in _AWS_SERVICES   if kw.lower() in lower)
    gcp_hits   = sum(1 for kw in _GCP_SERVICES   if kw.lower() in lower)
    op_hits    = sum(1 for kw in _ONPREM_FEATURES if kw.lower() in lower)

    # Explicit provider mention overrides keyword count
    if re.search(r'\bon[-\s]?prem(ises?)?\b', lower):
        providers.append("onprem")
    elif op_hits >= 3:
        providers.append("onprem")

    if re.search(r'\bazure\b', lower) or azure_hits >= 3:
        providers.append("azure")

    if re.search(r'\b(amazon web services|aws)\b', lower) or aws_hits >= 3:
        providers.append("aws")

    if re.search(r'\b(google cloud|gcp)\b', lower) or gcp_hits >= 3:
        providers.append("gcp")

    if not providers:
        # Last resort: any cloud mention
        if re.search(r'\bcloud\b', lower):
            providers.append("onprem")  # assume on-prem migration doc

    return providers or ["onprem"]


# ── Feature extraction ────────────────────────────────────────────────────────

# Function: _extract_features
def _extract_features(full_text: str, provider: str) -> dict[str, Any]:
    """Extract all features mentioned for the given provider."""
    lower = full_text.lower()
    features: dict[str, Any] = {"provider": provider, "found_services": [], "raw_specs": {}}

    if provider == "azure":
        features["found_services"] = [s for s in _AZURE_SERVICES if s.lower() in lower]
    elif provider == "aws":
        features["found_services"] = [s for s in _AWS_SERVICES if s.lower() in lower]
    elif provider == "gcp":
        features["found_services"] = [s for s in _GCP_SERVICES if s.lower() in lower]
    else:  # onprem
        features["found_services"] = [s for s in _ONPREM_FEATURES if s.lower() in lower]

    # Numeric specs
    cpu_matches  = _RE_CPU.findall(full_text)
    ram_matches  = _RE_RAM.findall(full_text)
    disk_matches = _RE_DISK.findall(full_text)

    features["raw_specs"] = {
        "cpu_values":  [int(v) for v in cpu_matches],
        "ram_gb_values": [float(v) for v in ram_matches],
        "disk_values": disk_matches,
        "ip_addresses": list(set(_RE_IP.findall(full_text))),
        "cidr_blocks":  list(set(_RE_CIDR.findall(full_text))),
        "hostnames":    _RE_HOSTNAME.findall(full_text),
        "os_mentions":  list(set(_RE_OS.findall(full_text))),
        "regions":      list(set(_RE_REGION.findall(full_text))),
        "environments": list(set(_RE_ENV.findall(full_text))),
    }

    # VM/instance type patterns
    az_vm  = re.findall(r'\b(Standard_[A-Z]\d+[a-z_]*(?:v\d)?)\b', full_text)
    aws_vm = re.findall(r'\b([a-z]\d[a-z]*\.\d*x?(?:large|medium|small|nano|micro))\b', full_text, re.IGNORECASE)
    gcp_vm = re.findall(r'\b(n\d-(?:standard|highmem|highcpu|custom)-\d+)\b', full_text, re.IGNORECASE)
    if az_vm:  features["raw_specs"]["azure_vm_skus"]   = list(set(az_vm))
    if aws_vm: features["raw_specs"]["aws_instance_types"] = list(set(aws_vm))
    if gcp_vm: features["raw_specs"]["gcp_machine_types"]  = list(set(gcp_vm))

    # Subnet/VLAN extraction
    subnets = list(set(_RE_CIDR.findall(full_text)))
    vlans = re.findall(r'VLAN\s*[:#]?\s*(\d{1,4})', full_text, re.IGNORECASE)
    if subnets: features["raw_specs"]["subnets"] = subnets
    if vlans:   features["raw_specs"]["vlans"] = list(set(vlans))

    # Storage tiers
    storage_tiers = re.findall(
        r'\b(Premium SSD|Standard SSD|Standard HDD|Ultra Disk|gp2|gp3|io1|io2|'
        r'sc1|st1|SSD|NVMe|HDD|SAN|NAS|Blob Hot|Blob Cool|Blob Archive)\b',
        full_text, re.IGNORECASE,
    )
    if storage_tiers:
        features["raw_specs"]["storage_tiers"] = list(set(storage_tiers))

    # Security/compliance mentions
    security = re.findall(
        r'\b(ISO 27001|SOC 2|PCI DSS|HIPAA|GDPR|FedRAMP|CIS Benchmark|NIST|'
        r'Zero Trust|MFA|Multi-Factor|TLS 1\.2|TLS 1\.3|AES-256|FIPS)\b',
        full_text, re.IGNORECASE,
    )
    if security:
        features["security_compliance"] = list(set(security))

    # HA/DR mentions
    ha_dr = re.findall(
        r'\b(High Availability|HA|Disaster Recovery|DR|RPO|RTO|Failover|'
        r'Multi-Region|Availability Zone|AZ|Active-Passive|Active-Active)\b',
        full_text, re.IGNORECASE,
    )
    if ha_dr:
        features["ha_dr_mentions"] = list(set(ha_dr))

    # Cost/capacity numbers
    server_counts = re.findall(r'(\d+)\s*(?:server|node|instance|host)s?', full_text, re.IGNORECASE)
    if server_counts:
        features["raw_specs"]["server_count_mentions"] = [int(n) for n in server_counts]

    return features


# ── Map extracted data to DiscoveredServer models ─────────────────────────────

# Function: _build_server_from_block
def _build_server_from_block(
    block: str,
    provider: str,
    doc_name: str,
    index: int,
) -> DiscoveredServer | None:
    """
    Attempt to build a DiscoveredServer from a text block that looks like a
    server entry (has CPU/RAM/hostname/IP signals).
    Returns None if insufficient information.
    """
    cpu_m = _RE_CPU.search(block)
    ram_m = _RE_RAM.search(block)
    host_m = _RE_HOSTNAME.search(block)
    ip_m  = _RE_IP.search(block)
    os_m  = _RE_OS.search(block)
    env_m = _RE_ENV.search(block)

    # Need at least hostname/IP + something useful
    if not (host_m or ip_m) and not (cpu_m and ram_m):
        return None

    s = DiscoveredServer()
    s.server_id     = str(uuid.uuid4())
    s.server_name   = host_m.group(1) if host_m else f"{provider.upper()}-{doc_name[:12]}-{index+1}"
    s.hostname      = s.server_name
    s.ip_address    = ip_m.group(1) if ip_m else ""
    s.cloud_provider = provider
    s.cpu_cores     = int(cpu_m.group(1)) if cpu_m else 0
    s.ram_gb        = float(ram_m.group(1)) if ram_m else 0.0
    s.os_name       = os_m.group(0).strip() if os_m else ""
    s.environment   = env_m.group(1).strip() if env_m else ""
    s.platform_host = f"PDF:{doc_name}"

    # Disk
    disk_m = _RE_DISK.search(block)
    if disk_m:
        val_str = disk_m.group(1)
        unit    = disk_m.group(0)
        gb_val  = float(val_str) * (1024 if "TB" in unit.upper() or "TiB" in unit.upper() else 1)
        s.disks = [DiskInfo(mount_point="/", size_gb=gb_val, disk_type="unknown")]
        s.total_storage_gb = gb_val

    # Region
    region_m = _RE_REGION.search(block)
    if region_m:
        s.region = region_m.group(0).strip()

    # Azure VM SKU
    az_sku = re.search(r'\b(Standard_[A-Z]\d+[a-z_]*(?:v\d)?)\b', block)
    if az_sku:
        s.instance_type = az_sku.group(1)
    # AWS instance
    aws_inst = re.search(r'\b([a-z]\d[a-z]*\.\d*x?(?:large|medium|small|nano|micro))\b', block, re.IGNORECASE)
    if aws_inst:
        s.instance_type = aws_inst.group(1)
    # GCP machine type
    gcp_m = re.search(r'\b(n\d-(?:standard|highmem|highcpu|custom)-\d+)\b', block, re.IGNORECASE)
    if gcp_m:
        s.instance_type = gcp_m.group(1)

    # Workloads from port/service mentions
    for service_pattern, (wl_type, wl_name) in [
        (r'\b(MySQL|MariaDB)\b', ("db", "MySQL")),
        (r'\bPostgreSQL\b', ("db", "PostgreSQL")),
        (r'\bSQL\s*Server\b', ("db", "MSSQL")),
        (r'\b(nginx|Apache)\b', ("web", "WebServer")),
        (r'\bTomcat\b', ("app", "ApacheTomcat")),
        (r'\bRedis\b', ("cache", "Redis")),
        (r'\bMongoDB\b', ("db", "MongoDB")),
        (r'\bRabbitMQ\b', ("queue", "RabbitMQ")),
        (r'\bKafka\b', ("queue", "Kafka")),
        (r'\bElasticsearch\b', ("search", "Elasticsearch")),
    ]:
        if re.search(service_pattern, block, re.IGNORECASE):
            wc = WorkloadComponent()
            wc.name = wl_name
            wc.component_type = wl_type
            s.workloads.append(wc)

    # Cloud suitability hints from text
    lower_block = block.lower()
    if any(kw in lower_block for kw in ["lift and shift", "rehost", "lift-and-shift"]):
        s.migration_strategy = "lift_and_shift"
    elif any(kw in lower_block for kw in ["refactor", "re-architect", "paas"]):
        s.migration_strategy = "paas_shift"
    elif any(kw in lower_block for kw in ["replatform", "smart shift"]):
        s.migration_strategy = "smart_shift"

    return s


# Function: _segment_into_server_blocks
def _segment_into_server_blocks(full_text: str) -> list[str]:
    """
    Split full document text into per-server blocks.
    Heuristic: look for section headers that indicate a server entry.
    Returns the full text as a single block if no structure is found,
    or splits on server/node/host headings.
    """
    # Try splitting on common server entry headers
    splits = re.split(
        r'(?m)^(?:Server|Node|Host|Machine|Instance|VM)\s*[:\-#]?\s*\d*\s*$|'
        r'(?:Server|Node|Host|Machine|Instance|VM)\s+Name\s*[:\-=]',
        full_text,
        flags=re.IGNORECASE,
    )
    if len(splits) > 1:
        return [s.strip() for s in splits if s.strip()]
    return [full_text]


# ── Main entry point ──────────────────────────────────────────────────────────

class PDFScanResult:
    """Container for one PDF document's scan output."""
    # Function: __init__
    def __init__(self, pdf_path: Path):
        self.pdf_name: str = pdf_path.name
        self.pdf_path: str = str(pdf_path)
        self.extraction_method: str = ""
        self.page_count: int = 0
        self.total_chars: int = 0
        self.detected_providers: list[str] = []
        self.features_by_provider: dict[str, Any] = {}
        self.servers: list[DiscoveredServer] = []
        self.error: str = ""


# Function: scan_pdf
def scan_pdf(pdf_path: Path, progress_cb: Any = None) -> PDFScanResult:
    """
    Full OCR + entity extraction pipeline for a single PDF.

    Args:
        pdf_path: path to the PDF file
        progress_cb: optional callback(message: str) for progress reporting

    Returns:
        PDFScanResult with all extracted infrastructure data
    """
    result = PDFScanResult(pdf_path)

    # Function: _progress
    def _progress(msg: str):
        log.info("[PDF] %s — %s", pdf_path.name, msg)
        if progress_cb:
            try:
                progress_cb(msg)
            except Exception:
                pass

    _progress("Starting text extraction")

    try:
        pages, method = _extract_all_text(pdf_path)
    except Exception as exc:
        result.error = f"Text extraction failed: {exc}"
        log.error("PDF scan failed for %s: %s", pdf_path.name, exc)
        return result

    result.extraction_method = method
    result.page_count = len(pages)
    full_text = "\n\n".join(pages)
    result.total_chars = len(full_text)

    if result.total_chars < 50:
        result.error = "No readable text extracted from PDF (possibly empty or image-only without OCR deps)"
        return result

    _progress(f"Extracted {result.total_chars:,} chars from {result.page_count} pages via {method}")

    # Provider detection
    providers = _detect_providers(full_text)
    result.detected_providers = providers
    _progress(f"Detected providers: {', '.join(providers)}")

    # Feature extraction per provider
    for provider in providers:
        features = _extract_features(full_text, provider)
        result.features_by_provider[provider] = features
        _progress(
            f"[{provider.upper()}] Found {len(features['found_services'])} services/features"
        )

    # Build DiscoveredServer objects
    _progress("Mapping extracted data to infrastructure models")
    blocks = _segment_into_server_blocks(full_text)
    primary_provider = providers[0]

    for i, block in enumerate(blocks):
        server = _build_server_from_block(block, primary_provider, pdf_path.stem, i)
        if server:
            result.servers.append(server)

    # If no structured blocks found, create a summary server record
    if not result.servers:
        s = DiscoveredServer()
        s.server_id      = str(uuid.uuid4())
        s.server_name    = f"DOC-{pdf_path.stem[:20]}"
        s.hostname       = s.server_name
        s.cloud_provider = primary_provider
        s.platform_host  = f"PDF:{pdf_path.name}"

        # Use first found specs
        for provider_features in result.features_by_provider.values():
            specs = provider_features.get("raw_specs", {})
            if specs.get("cpu_values"):
                s.cpu_cores = max(specs["cpu_values"])
            if specs.get("ram_gb_values"):
                s.ram_gb = max(specs["ram_gb_values"])
            if specs.get("hostnames"):
                s.server_name = specs["hostnames"][0]
                s.hostname = s.server_name
            if specs.get("ip_addresses"):
                s.ip_address = specs["ip_addresses"][0]
            if specs.get("os_mentions"):
                s.os_name = specs["os_mentions"][0]
            if specs.get("regions"):
                s.region = specs["regions"][0]
            if specs.get("environments"):
                s.environment = specs["environments"][0]
            if specs.get("azure_vm_skus"):
                s.instance_type = specs["azure_vm_skus"][0]
            elif specs.get("aws_instance_types"):
                s.instance_type = specs["aws_instance_types"][0]
            elif specs.get("gcp_machine_types"):
                s.instance_type = specs["gcp_machine_types"][0]

        result.servers.append(s)

    _progress(f"Extracted {len(result.servers)} server record(s)")
    return result


# Function: scan_data_directory
def scan_data_directory(
    data_dir: Path | str,
    progress_cb: Any = None,
) -> list[PDFScanResult]:
    """
    Scan all PDF files found in data_dir (recursively).
    Returns a list of PDFScanResult objects.
    """
    data_dir = Path(data_dir)
    pdf_files = sorted(data_dir.rglob("*.pdf"))

    if not pdf_files:
        log.warning("No PDF files found in %s", data_dir)
        return []

    log.info("Found %d PDF files to scan in %s", len(pdf_files), data_dir)
    results = []

    for pdf_path in pdf_files:
        log.info("Scanning PDF: %s", pdf_path.name)
        if progress_cb:
            try:
                progress_cb(f"Scanning {pdf_path.name}…")
            except Exception:
                pass
        result = scan_pdf(pdf_path, progress_cb=progress_cb)
        results.append(result)

    return results


# Function: build_pdf_scan_report
def build_pdf_scan_report(results: list[PDFScanResult]) -> dict[str, Any]:
    """
    Build a consolidated report dict from all PDF scan results.
    Compatible with the existing scan report format.
    """
    all_servers = []
    all_providers: set[str] = set()
    pdf_features: list[dict] = []
    total_services_found: list[str] = []

    for r in results:
        all_providers.update(r.detected_providers)

        doc_summary = {
            "pdf_name": r.pdf_name,
            "extraction_method": r.extraction_method,
            "page_count": r.page_count,
            "total_chars": r.total_chars,
            "detected_providers": r.detected_providers,
            "error": r.error,
            "servers_extracted": len(r.servers),
            "features_by_provider": r.features_by_provider,
        }
        pdf_features.append(doc_summary)

        for provider_feats in r.features_by_provider.values():
            total_services_found.extend(provider_feats.get("found_services", []))

        for srv in r.servers:
            d = asdict(srv)
            # Flatten DiskInfo/NetworkInterface/WorkloadComponent lists
            d["disks"] = [asdict(dk) for dk in srv.disks]
            d["interfaces"] = [asdict(ni) for ni in srv.interfaces]
            d["workloads"] = [asdict(wc) for wc in srv.workloads]
            d["installed_software"] = [asdict(sw) for sw in srv.installed_software]
            all_servers.append(d)

    # De-duplicate services list
    from collections import Counter
    service_counts = Counter(total_services_found)
    top_services = [{"service": k, "mention_count": v} for k, v in service_counts.most_common(50)]

    return {
        "report_type": "pdf_ocr_scan",
        "documents_scanned": len(results),
        "detected_providers": sorted(all_providers),
        "total_servers_extracted": len(all_servers),
        "servers": all_servers,
        "pdf_documents": pdf_features,
        "top_services_mentioned": top_services,
        "summary": {
            "providers": sorted(all_providers),
            "total_services_identified": len(set(total_services_found)),
            "total_servers": len(all_servers),
            "documents": len(results),
        },
    }
