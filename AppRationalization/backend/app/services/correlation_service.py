# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: AppRationalization — backend/app/services (correlation_service.py)
# Date: 2026-02-24
# ---------------------------------------------------------------------------
import json
import datetime
from typing import Dict, List, Any, Tuple, Optional
from difflib import SequenceMatcher

from app import db
from app.models.corent_data import CorentData
from app.models.cast import CASTData, ApplicationInventory
from app.models.correlation import CorrelationResult, MasterMatrixEntry
from app.models.industry_data import IndustryData

# ---------------------------------------------------------------------------
# Module-level matching constants
# ---------------------------------------------------------------------------
_CONFIDENCE_DIRECT: float = 1.0
_CONFIDENCE_HIGH: float = 0.85
_CONFIDENCE_MIN: float = 0.6


# ---------------------------------------------------------------------------
# Infrastructure / CAST data-structure builders (used by correlate_data)
# ---------------------------------------------------------------------------

# Function: _build_infra_data
def _build_infra_data(industry_items, corent_items):
    infra_data: Dict[str, Any] = {
        "source": "Industry + Corent",
        "report_type": "infrastructure",
        "items_by_app_id": {},
        "total_items": len(industry_items) + len(corent_items),
        "tech_stack": {},
        "deployment_footprint": {},
        "server_app_mapping": [],
        "server_list": set(),
    }

    for item in industry_items:
        app_id = item.app_id
        entry = {
            "app_id": item.app_id,
            "app_name": item.app_name,
            "architecture_type": getattr(item, "architecture_type", None),
            "business_owner": getattr(item, "business_owner", None),
            "platform_host": getattr(item, "platform_host", None),
            "server_type": getattr(item, "server_type", None) or getattr(item, "application_type", None),
            "operating_system": getattr(item, "operating_system", None),
            "environment": getattr(item, "environment", None),
            "cloud_suitability": getattr(item, "cloud_suitability", None),
            "ha_dr_requirements": getattr(item, "ha_dr_requirements", None),
            "installed_tech": getattr(item, "server_type", None) or getattr(item, "application_type", None),
            "server": getattr(item, "platform_host", None) or "Unknown",
            "source": "IndustryData",
        }
        infra_data["items_by_app_id"][app_id] = entry
        infra_data["server_app_mapping"].append(entry)

    corent_by_server_name: Dict[str, Any] = {}
    for item in corent_items:
        server_name = item.server_name or ""
        synthetic_key = f"corent_{server_name}" if server_name else f"corent_{item.id}"
        app_name = server_name or f"CORENT-Server-{item.id}"
        if synthetic_key not in infra_data["items_by_app_id"]:
            entry = {
                "app_id": synthetic_key,
                "app_name": app_name,
                "server_name": server_name,
                "architecture_type": item.architecture_type,
                "business_owner": item.business_owner,
                "platform_host": item.platform_host,
                "server_type": item.server_type,
                "operating_system": item.operating_system,
                "environment": item.environment,
                "cloud_suitability": item.cloud_suitability,
                "ha_dr_requirements": item.ha_dr_requirements,
                "installed_tech": item.server_type,
                "server": item.platform_host or server_name or "Unknown",
                "source": "CorentData",
                "corent_record_id": item.id,
            }
            infra_data["items_by_app_id"][synthetic_key] = entry
            infra_data["server_app_mapping"].append(entry)
        if server_name:
            corent_by_server_name[server_name.lower()] = infra_data["items_by_app_id"][synthetic_key]

    infra_data["total_items"] = len(infra_data["items_by_app_id"])
    return infra_data, corent_by_server_name


# Function: _build_cast_data_for_correlation
def _build_cast_data_for_correlation(cast_items, industry_type_by_app_id, determine_lang_fn):
    cast_data: Dict[str, Any] = {
        "source": "CAST",
        "report_type": "code_analysis",
        "items_by_app_id": {},
        "total_items": len(cast_items),
        "programming_languages": {},
        "cloud_readiness_distribution": {},
        "repo_app_mapping": [],
        "architecture_components": [],
        "internal_dependencies": {},
    }

    for item in cast_items:
        app_id = item.app_id
        determined_language = determine_lang_fn(
            item.app_name, item.app_id, industry_type_by_app_id.get(app_id),
        )
        cast_entry = {
            "app_id": item.app_id,
            "app_name": item.app_name,
            "server_name": item.server_name or "",
            "application_architecture": item.application_architecture,
            "source_code_availability": item.source_code_availability,
            "programming_language": determined_language,
            "component_coupling": item.component_coupling,
            "cloud_suitability": item.cloud_suitability,
            "volume_external_dependencies": item.volume_external_dependencies,
            "code_design": item.code_design,
            "from_cast_data": True,
            "language": determined_language,
            "repo": f"repo/{item.app_id}",
            "framework": item.application_architecture or "N/A",
        }
        cast_data["items_by_app_id"][app_id] = cast_entry
        cast_data["repo_app_mapping"].append(cast_entry)
        cast_data["architecture_components"].append(cast_entry)

        if determined_language:
            cast_data["programming_languages"][determined_language] = (
                cast_data["programming_languages"].get(determined_language, 0) + 1
            )
        if item.cloud_suitability:
            cast_data["cloud_readiness_distribution"][item.cloud_suitability] = (
                cast_data["cloud_readiness_distribution"].get(item.cloud_suitability, 0) + 1
            )
        if item.volume_external_dependencies:
            cast_data["internal_dependencies"][app_id] = {
                "app_name": item.app_name,
                "dependency_count": item.volume_external_dependencies,
            }

    return cast_data


# Function: _phase_server_name_match
def _phase_server_name_match(
    unmatched_cast, unmatched_infra, corent_by_server_name,
    matched_infra_app_ids, matched_cast_app_ids,
):
    server_name_matches: List[Dict[str, Any]] = []
    avail_corent_by_sname = {
        k: v for k, v in corent_by_server_name.items()
        if v["app_id"] not in matched_infra_app_ids
    }
    for cast_app_id, cast_item in list(unmatched_cast.items()):
        cast_sname = (cast_item.get("server_name") or "").strip().lower()
        if not cast_sname:
            continue
        corent_entry = avail_corent_by_sname.get(cast_sname)
        if corent_entry:
            server_name_matches.append({
                "infra_item": corent_entry,
                "cast_item": cast_item,
                "confidence": 0.9,
                "matching_criteria": [f"Server name match: {cast_item['server_name']}"],
                "confidence_level": "high",
                "app_id": cast_app_id,
                "match_type": "server_name",
            })
            matched_infra_app_ids.add(corent_entry["app_id"])
            matched_cast_app_ids.add(cast_app_id)
            del unmatched_infra[corent_entry["app_id"]]
            del unmatched_cast[cast_app_id]
            del avail_corent_by_sname[cast_sname]
    return server_name_matches


# Function: _phase_exact_name_match
def _phase_exact_name_match(
    unmatched_infra, unmatched_cast, matched_infra_app_ids, matched_cast_app_ids,
):
    exact_name_matches: List[Dict[str, Any]] = []
    cast_by_exact_name: Dict[str, Any] = {
        (ci.get("app_name") or "").strip().lower(): ci
        for ci in unmatched_cast.values()
        if (ci.get("app_name") or "").strip()
    }
    for infra_app_id, infra_item in list(unmatched_infra.items()):
        infra_name = (infra_item.get("app_name") or "").strip().lower()
        if not infra_name:
            continue
        cast_item = cast_by_exact_name.get(infra_name)
        if cast_item:
            exact_name_matches.append({
                "infra_item": infra_item,
                "cast_item": cast_item,
                "confidence": 0.95,
                "matching_criteria": [f"App name exact match: {infra_item['app_name']}"],
                "confidence_level": "high",
                "app_id": infra_app_id,
                "match_type": "app_name_exact",
            })
            matched_infra_app_ids.add(infra_app_id)
            matched_cast_app_ids.add(cast_item["app_id"])
            del unmatched_infra[infra_app_id]
            del unmatched_cast[cast_item["app_id"]]
            del cast_by_exact_name[infra_name]
    return exact_name_matches


# Function: _find_best_fuzzy_match
def _find_best_fuzzy_match(infra_name, cast_names_normalised, unmatched_cast):
    infra_len = len(infra_name)
    best_match = None
    best_confidence = 0.0
    best_cast_app_id = None

    for cast_app_id, cast_name in cast_names_normalised.items():
        if not cast_name:
            continue
        cast_len = len(cast_name)
        ratio = infra_len / cast_len if cast_len else 0
        if ratio < 0.4 or ratio > 2.5:
            continue
        name_sim = SequenceMatcher(None, infra_name, cast_name).ratio()
        if name_sim >= _CONFIDENCE_MIN and name_sim > best_confidence:
            best_match = unmatched_cast[cast_app_id]
            best_confidence = name_sim
            best_cast_app_id = cast_app_id
            if best_confidence >= _CONFIDENCE_HIGH:
                break

    return best_match, best_confidence, best_cast_app_id


# Function: _phase_fuzzy_match
def _phase_fuzzy_match(unmatched_infra, unmatched_cast):
    cast_names_normalised: Dict[str, str] = {
        cast_app_id: (cast_item.get("app_name") or "").strip().lower()
        for cast_app_id, cast_item in unmatched_cast.items()
    }
    fuzzy_matches: List[Dict[str, Any]] = []
    for infra_app_id, infra_item in list(unmatched_infra.items()):
        infra_name = (infra_item.get("app_name") or "").strip().lower()
        if not infra_name:
            continue

        best_match, best_confidence, best_cast_app_id = _find_best_fuzzy_match(
            infra_name, cast_names_normalised, unmatched_cast
        )

        if best_match:
            fuzzy_matches.append({
                "infra_item": infra_item,
                "cast_item": best_match,
                "confidence": round(best_confidence, 3),
                "matching_criteria": [f"App name fuzzy match ({best_confidence:.2f})"],
                "confidence_level": "medium" if best_confidence >= 0.8 else "low",
                "app_id": infra_app_id,
                "match_type": "fuzzy",
            })
            del unmatched_infra[infra_app_id]
            del unmatched_cast[best_cast_app_id]
            del cast_names_normalised[best_cast_app_id]
    return fuzzy_matches


# Function: _run_all_matching_phases
def _run_all_matching_phases(infra_data, cast_data, corent_by_server_name):
    direct_matches: List[Dict[str, Any]] = []
    matched_infra_app_ids: set = set()
    matched_cast_app_ids: set = set()

    for app_id, infra_item in infra_data["items_by_app_id"].items():
        if app_id in cast_data["items_by_app_id"]:
            cast_item = cast_data["items_by_app_id"][app_id]
            direct_matches.append({
                "infra_item": infra_item,
                "cast_item": cast_item,
                "confidence": _CONFIDENCE_DIRECT,
                "matching_criteria": ["Direct APP ID match"],
                "confidence_level": "high",
                "app_id": app_id,
                "match_type": "direct",
            })
            matched_infra_app_ids.add(app_id)
            matched_cast_app_ids.add(app_id)

    unmatched_infra = {
        k: v for k, v in infra_data["items_by_app_id"].items()
        if k not in matched_infra_app_ids
    }
    unmatched_cast = {
        k: v for k, v in cast_data["items_by_app_id"].items()
        if k not in matched_cast_app_ids
    }
    truly_unmatched_corent = dict(unmatched_infra)
    truly_unmatched_cast = dict(unmatched_cast)

    # Phase 1b: server_name exact match
    server_name_matches = _phase_server_name_match(
        unmatched_cast, unmatched_infra, corent_by_server_name,
        matched_infra_app_ids, matched_cast_app_ids,
    )

    # Phase 1c: app name exact match
    exact_name_matches = _phase_exact_name_match(
        unmatched_infra, unmatched_cast, matched_infra_app_ids, matched_cast_app_ids,
    )

    # Phase 2: fuzzy app_name match
    fuzzy_matches = _phase_fuzzy_match(unmatched_infra, unmatched_cast)

    return (
        direct_matches, server_name_matches, exact_name_matches, fuzzy_matches,
        unmatched_infra, unmatched_cast, truly_unmatched_corent, truly_unmatched_cast,
    )


# ---------------------------------------------------------------------------
# Master-matrix entry builders (used by generate_master_matrix)
# ---------------------------------------------------------------------------

# Function: _make_matched_entry
def _make_matched_entry(match: Dict[str, Any]) -> Dict[str, Any]:
    infra = match["infra_item"]
    cast  = match["cast_item"]
    repository = cast.get("repository", "") or cast.get("repo", "")
    entry = {
        "app_id": match.get("app_id", ""),
        "app_name": infra.get("app_name", "") or cast.get("app_name", ""),
        "infrastructure": infra.get("platform_host", ""),
        "server_type": infra.get("server_type", ""),
        "installed_app": infra.get("app_name", ""),
        "environment": infra.get("environment", ""),
        "app_component": (
            f"{cast.get('programming_language', '')} - {cast.get('framework', '')}".strip(" - ")
        ),
        "repository": repository,
        "business_owner": infra.get("business_owner", ""),
        "cloud_suitability_corent": infra.get("cloud_suitability", ""),
        "cloud_suitability_cast": cast.get("cloud_suitability", ""),
        "confidence": match["confidence"],
        "confidence_level": match["confidence_level"],
        "match_type": match.get("match_type", "unknown"),
        "matching_criteria": " | ".join(match["matching_criteria"]),
    }
    entry["infra"]   = entry["infrastructure"]
    entry["server"]  = entry["server_type"]
    entry["repo"]    = entry["repository"]
    return entry


# Function: _make_unmatched_infra_entry
def _make_unmatched_infra_entry(infra_item: Dict[str, Any]) -> Dict[str, Any]:
    entry = {
        "app_id": infra_item.get("app_id", ""),
        "app_name": infra_item.get("app_name", ""),
        "infrastructure": infra_item.get("platform_host", ""),
        "server_type": infra_item.get("server_type", ""),
        "installed_app": infra_item.get("app_name", ""),
        "environment": infra_item.get("environment", ""),
        "app_component": "Unmatched - No CAST data",
        "repository": "",
        "business_owner": infra_item.get("business_owner", ""),
        "cloud_suitability_corent": infra_item.get("cloud_suitability", ""),
        "cloud_suitability_cast": "",
        "confidence": 0.0,
        "confidence_level": "unmatched",
        "match_type": "unmatched",
        "matching_criteria": "No CAST correlation found",
    }
    entry["infra"]   = entry["infrastructure"]
    entry["server"]  = entry["server_type"]
    entry["repo"]    = entry["repository"]
    return entry


# Function: _make_unmatched_cast_entry
def _make_unmatched_cast_entry(cast_item: Dict[str, Any]) -> Dict[str, Any]:
    repository = cast_item.get("repository", "") or cast_item.get("repo", "")
    entry = {
        "app_id": cast_item.get("app_id", ""),
        "app_name": cast_item.get("app_name", ""),
        "infrastructure": "",
        "server_type": "",
        "installed_app": "",
        "environment": "",
        "app_component": (
            f"{cast_item.get('programming_language', '')} - {cast_item.get('framework', '')}".strip(" - ")
        ),
        "repository": repository,
        "business_owner": "",
        "cloud_suitability_corent": "",
        "cloud_suitability_cast": cast_item.get("cloud_suitability", ""),
        "confidence": 0.0,
        "confidence_level": "unmatched",
        "match_type": "unmatched",
        "matching_criteria": "No Corent correlation found",
    }
    entry["infra"]   = entry["infrastructure"]
    entry["server"]  = entry["server_type"]
    entry["repo"]    = entry["repository"]
    return entry


# Function: _build_corent_entry
def _build_corent_entry(item):
    """Build the normalized entry dict for a CorentData/IndustryData item."""
    return {
        "app_id": item.app_id,
        "app_name": item.app_name,
        "architecture_type": getattr(item, 'architecture_type', None),
        "business_owner": getattr(item, 'business_owner', None),
        "platform_host": getattr(item, 'platform_host', None),
        "server_type": getattr(item, 'server_type', None) or getattr(item, 'application_type', None),
        "operating_system": getattr(item, 'operating_system', None),
        "environment": getattr(item, 'environment', None),
        "cloud_suitability": getattr(item, 'cloud_suitability', None),
        "ha_dr_requirements": getattr(item, 'ha_dr_requirements', None),
        "installed_tech": getattr(item, 'server_type', None) or getattr(item, 'application_type', None),
        "server": getattr(item, 'platform_host', None) or "Unknown",
    }


# Function: _resolve_corent_deployment
def _resolve_corent_deployment(item, corent_item):
    """Resolve deployment geography, falling back to the legacy CorentData record."""
    deployment = getattr(item, 'deployment_geography', None) or getattr(item, 'environment', None)
    if not deployment and corent_item:
        deployment = getattr(corent_item, 'deployment_geography', None) or getattr(corent_item, 'environment', None)
    return deployment


# Function: _accumulate_corent_item
def _accumulate_corent_item(item, corent_map, data):
    """Build the entry for one Corent/Industry item and fold it into the aggregate `data` dict."""
    app_id = item.app_id
    corent_item = corent_map.get(app_id)
    entry = _build_corent_entry(item)

    data["items_by_app_id"][app_id] = entry
    data["server_app_mapping"].append(entry)

    tech = entry["server_type"]
    if tech:
        data["tech_stack"][tech] = data["tech_stack"].get(tech, 0) + 1

    deployment = _resolve_corent_deployment(item, corent_item)
    if deployment:
        data["deployment_footprint"][deployment] = data["deployment_footprint"].get(deployment, 0) + 1

    server = getattr(item, 'platform_host', None)
    if server:
        data["server_list"].add(server)


# Function: _load_cast_items_into_data
def _load_cast_items_into_data(cast_items, cast_data, industry_type_by_app_id, determine_lang_fn):
    for item in cast_items:
        app_id = item.app_id
        prog_language = determine_lang_fn(
            item.app_name,
            app_id,
            industry_type_by_app_id.get(app_id),
        )
        cast_entry = {
            "app_id": item.app_id,
            "app_name": item.app_name,
            "application_architecture": item.application_architecture,
            "source_code_availability": item.source_code_availability,
            "programming_language": prog_language,
            "component_coupling": item.component_coupling,
            "cloud_suitability": item.cloud_suitability,
            "volume_external_dependencies": item.volume_external_dependencies,
            "code_design": item.code_design,
            "from_cast_data": True,
            "language": prog_language,
            "repo": f"repo/{item.app_id}",
            "framework": item.application_architecture or "N/A",
        }
        cast_data["items_by_app_id"][app_id] = cast_entry
        cast_data["repo_app_mapping"].append(cast_entry)
        cast_data["architecture_components"].append(cast_entry)
        cast_data["programming_languages"][prog_language] = (
            cast_data["programming_languages"].get(prog_language, 0) + 1
        )
        if item.cloud_suitability:
            cast_data["cloud_readiness_distribution"][item.cloud_suitability] = (
                cast_data["cloud_readiness_distribution"].get(item.cloud_suitability, 0) + 1
            )
        if item.volume_external_dependencies:
            cast_data["internal_dependencies"][app_id] = {
                "app_name": item.app_name,
                "dependency_count": item.volume_external_dependencies
            }


# Function: _merge_app_inventories_into_cast
def _merge_app_inventories_into_cast(app_inventories, cast_data):
    for item in app_inventories:
        app_id = item.app_id
        app_inv_entry = {
            "app_id": item.app_id,
            "app_name": item.application or item.app_id,
            "repository": item.repo,
            "repo": item.repo,
            "primary_language": item.primary_language,
            "language": item.primary_language,
            "framework": item.framework,
            "loc_k": item.loc_k,
            "modules": item.modules,
            "database": item.db_name,
            "external_integrations": item.ext_int,
            "quality": item.quality,
            "security": item.security,
            "cloud_ready": item.cloud_ready,
            "from_app_inventory": True,
            "type": "Microservice"
        }
        if app_id in cast_data["items_by_app_id"]:
            cast_data["items_by_app_id"][app_id].update(app_inv_entry)
            for component in cast_data["architecture_components"]:
                if component["app_id"] == app_id:
                    component.update(app_inv_entry)
                    break
        else:
            cast_data["items_by_app_id"][app_id] = app_inv_entry
            cast_data["architecture_components"].append(app_inv_entry)
        cast_data["repo_app_mapping"].append(app_inv_entry)


class CorrelationService:
    """
    Service to correlate Corent (Infrastructure) and CAST (Code Analysis) extracted data.
    
    Primary matching strategy:
    - Uses APP ID as the primary key/relationship between the two databases
    - Direct APP ID matching provides high confidence correlations (1.0)
    - Fuzzy matching on app names used as fallback for unmatched items
    """
    
    # Matching confidence thresholds (reference module-level constants)
    MIN_CONFIDENCE = _CONFIDENCE_MIN
    HIGH_CONFIDENCE = _CONFIDENCE_HIGH
    DIRECT_MATCH_CONFIDENCE = _CONFIDENCE_DIRECT
    
    # Function: get_corent_data
    @staticmethod
    def get_corent_data() -> Dict[str, Any]:
        """
        Fetch Corent (Infrastructure) data - prioritizes IndustryData if available.
        Uses APP ID as primary identifier.
        
        Returns:
            Dictionary with structured infrastructure data indexed by APP ID
        """
        # Prioritize IndustryData if available
        industry_items = IndustryData.query.all()
        if industry_items:
            items = industry_items
            source = "Industry Templates"
        else:
            items = CorentData.query.all()
            source = "Corent"
        
        # Build CorentData mapping for lookups when using IndustryData
        corent_map = {}  # app_id/app_name removed from CorentData
        
        data = {
            "source": source,
            "report_type": "infrastructure",
            "items_by_app_id": {},  # Indexed by APP ID for fast lookup
            "total_items": len(items),
            "tech_stack": {},
            "deployment_footprint": {},  # Geographic/environment distribution
            "server_app_mapping": [],  # For dashboard display
            "server_list": set()
        }
        
        for item in items:
            _accumulate_corent_item(item, corent_map, data)

        # Convert sets to lists for JSON serialization
        data["server_list"] = list(data["server_list"])

        return data
    
    # Function: get_cast_data
    @staticmethod
    def get_cast_data() -> Dict[str, Any]:
        """
        Fetch CAST (Code Analysis) data from CASTData and ApplicationInventory models.
        Uses APP ID as primary identifier.
        
        Returns:
            Dictionary with structured CAST data indexed by APP ID
        """
        cast_items = CASTData.query.all()
        app_inventories = ApplicationInventory.query.all()
        # Pre-index all IndustryData by app_id in ONE query — avoids N+1 (one query per CAST item)
        industry_type_by_app_id: Dict[str, Any] = {
            i.app_id: i.application_type for i in IndustryData.query.all()
        }

        cast_data = {
            "source": "CAST",
            "report_type": "code_analysis",
            "items_by_app_id": {},
            "total_items": len(cast_items),
            "programming_languages": {},
            "cloud_readiness_distribution": {},
            "repo_app_mapping": [],
            "architecture_components": [],
            "internal_dependencies": {}
        }

        # Load CAST Data (aggregated metrics)
        _load_cast_items_into_data(
            cast_items, cast_data, industry_type_by_app_id,
            CorrelationService.determine_programming_language,
        )

        # Load ApplicationInventory (detailed code-level analysis)
        _merge_app_inventories_into_cast(app_inventories, cast_data)

        return cast_data
    
    
    # Function: determine_programming_language
    @staticmethod
    def determine_programming_language(app_name: str, app_id: str, application_type: str = None) -> str:
        """
        Determine programming language based on app name patterns and type.
        Uses heuristics to assign realistic languages for test data.
        
        Args:
            app_name: Application name
            app_id: Application ID
            application_type: Type of application (e.g., "Commercial off the shelf")
            
        Returns:
            Programming language name
        """
        app_name_lower = (app_name or '').lower()

        language_rules = [
            ('PHP', ['php', 'laravel', 'wordpress']),
            ('Python', ['python', 'django', 'flask']),
            ('Java', ['java', 'spring', 'tomcat']),
            ('JavaScript/Node.js', ['node', 'express', 'react', 'vue', 'javascript']),
            ('C#/.NET', ['.net', 'csharp', 'c#', 'aspnet', 'dotnet']),
            ('Go', ['go', 'golang']),
            ('Rust', ['rust']),
            ('Ruby', ['ruby', 'rails']),
            ('C++', ['cpp', 'c++', 'native']),
            ('Go', ['bitcoin', 'crypto', 'blockchain']),  # Popular for blockchain
        ]
        for language, patterns in language_rules:
            if any(pattern in app_name_lower for pattern in patterns):
                return language

        # Default based on application type
        if application_type:
            app_type_lower = application_type.lower()
            if 'commercial' in app_type_lower:
                return 'Java' if 'major' in app_type_lower else 'C#/.NET'
            if 'self' in app_type_lower:
                return 'Python'
        
        # Distribute remaining apps across common languages
        hash_value = sum(ord(c) for c in app_id) % 5
        languages = ['Java', 'Python', 'C#/.NET', 'JavaScript/Node.js', 'Go']
        return languages[hash_value]
    
    # Function: string_similarity
    @staticmethod
    def string_similarity(s1: str, s2: str) -> float:
        """
        Calculate string similarity score (0.0 - 1.0).
        
        Args:
            s1: First string
            s2: Second string
            
        Returns:
            Similarity score
        """
        s1 = str(s1).strip().lower()
        s2 = str(s2).strip().lower()
        
        if not s1 or not s2:
            return 0.0
        
        return SequenceMatcher(None, s1, s2).ratio()
    
    # Function: correlate_data
    @staticmethod
    def correlate_data() -> Dict[str, Any]:
        """
        Correlate data from ALL THREE sources: Industry, Corent, and CAST data.
        
        Strategy:
        1. Combine IndustryData + CorentData as the infrastructure layer (all records from both)
        2. Get CAST data for code analysis layer
        3. Attempt to match records by APP ID first, then by name similarity
        
        Returns:
            Dictionary with correlation results from all three data sources
        """
        industry_items = IndustryData.query.all()
        corent_items   = CorentData.query.all()
        cast_items     = CASTData.query.all()

        infra_data, corent_by_server_name = _build_infra_data(industry_items, corent_items)

        industry_type_by_app_id: Dict[str, Any] = {
            i.app_id: i.application_type for i in industry_items
        }
        cast_data = _build_cast_data_for_correlation(
            cast_items, industry_type_by_app_id,
            CorrelationService.determine_programming_language,
        )

        (
            direct_matches, server_name_matches, exact_name_matches, fuzzy_matches,
            unmatched_infra, unmatched_cast, truly_unmatched_corent, truly_unmatched_cast,
        ) = _run_all_matching_phases(infra_data, cast_data, corent_by_server_name)

        correlation_layer = direct_matches + server_name_matches + exact_name_matches + fuzzy_matches
        all_matched = len(correlation_layer)

        app_total = len(industry_items) if industry_items else len(corent_items)
        cast_total = cast_data["total_items"]
        match_denom = max(app_total, cast_total, 1)

        return {
            "corent_dashboard": infra_data,
            "cast_dashboard": cast_data,
            "correlation_layer": correlation_layer,
            "direct_matches": direct_matches,
            "server_name_matches": server_name_matches,
            "exact_name_matches": exact_name_matches,
            "fuzzy_matches": fuzzy_matches,
            "unmatched_corent": list(truly_unmatched_corent.values()),
            "unmatched_cast": list(truly_unmatched_cast.values()),
            "statistics": {
                # Application-level counts (shown in Overview cards)
                "industry_total": len(industry_items),
                "corent_server_total": len(corent_items),
                "corent_total": app_total,          # = IndustryData apps (primary app count)
                "cast_total": cast_total,
                # Match breakdown by phase
                "direct_matched": len(direct_matches),
                "server_name_matched": len(server_name_matches),
                "exact_name_matched": len(exact_name_matches),
                "fuzzy_matched": len(fuzzy_matches),
                # Totals
                "total_matched": all_matched,       # all phases combined
                "correlated_total": all_matched,
                "unmatched_corent_count": len(truly_unmatched_corent),
                "unmatched_cast_count": len(truly_unmatched_cast),
                # Store the exact denominator used for match_percentage so downstream
                # consumers (create_correlation_result) can keep total_count and
                # match_percentage arithmetically consistent — previously total_count
                # was hardcoded to corent_total/app_total while match_percentage used
                # max(app_total, cast_total, 1), so "X of Y matched (Z%)" could show a
                # Z that didn't equal X/Y when app_total != cast_total.
                "match_denom": match_denom,
                "match_percentage": round((all_matched / match_denom) * 100, 2),
            },
        }

    
    # Function: generate_master_matrix
    @staticmethod
    def generate_master_matrix(correlation_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate master matrix combining Corent and CAST data.
        
        Master matrix columns:
        - App Name: Application identifier
        - Infrastructure: Server/hostname from Corent
        - Server Type: Domain/environment from Corent
        - Installed App: Application name from Corent
        - App Component: Framework/language from CAST
        - Repository: Code repository from CAST
        - Cloud Suitability: Cloud readiness from both sources
        - Confidence: Correlation confidence score (1.0 for direct APP ID match)
        
        Args:
            correlation_data: Output from correlate_data()
            
        Returns:
            List of master matrix entries with complete app information
        """
        master_matrix = []
        for match in correlation_data.get("correlation_layer", []):
            master_matrix.append(_make_matched_entry(match))
        for infra_item in (correlation_data.get("unmatched_corent") or correlation_data.get("unmatched_infra", [])):
            master_matrix.append(_make_unmatched_infra_entry(infra_item))
        for cast_item in correlation_data.get("unmatched_cast", []):
            master_matrix.append(_make_unmatched_cast_entry(cast_item))
        return master_matrix
    
    # Function: create_correlation_result
    @classmethod
    def create_correlation_result(cls, correlation_data: Dict[str, Any]) -> CorrelationResult:
        """
        Create and store correlation result in database.
        
        Args:
            correlation_data: Output from correlate_data()
            
        Returns:
            CorrelationResult database object with stored master matrix entries
        """
        master_matrix = cls.generate_master_matrix(correlation_data)
        
        stats = correlation_data.get("statistics", {})
        # Create main correlation result record
        result = CorrelationResult(
            correlation_data=json.dumps(correlation_data, default=str),
            master_matrix=json.dumps(master_matrix, default=str),
            matched_count=stats.get("total_matched", stats.get("correlated_total", 0)),
            # Use the same denominator match_percentage was computed against, not
            # corent_total specifically — otherwise "X of Y matched (Z%)" can display
            # a Z that doesn't equal X/Y whenever app_total != cast_total.
            total_count=stats.get("match_denom") or stats.get("corent_total", 0),
            match_percentage=stats.get("match_percentage", 0.0)
        )
        
        db.session.add(result)
        db.session.flush()  # Populate result.id before bulk-inserting child rows

        # Bulk-insert all MasterMatrixEntry rows in one round-trip instead of N individual INSERTs
        db.session.bulk_save_objects([
            MasterMatrixEntry(
                correlation_result_id=result.id,
                app_name=entry_data.get("app_name", ""),
                infra=entry_data.get("infrastructure", ""),
                server=entry_data.get("server_type", ""),
                installed_app=entry_data.get("installed_app", ""),
                app_component=entry_data.get("app_component", ""),
                repo=entry_data.get("repository", ""),
                confidence=entry_data.get("confidence", 0.0),
                entry_data=json.dumps(entry_data, default=str),
            )
            for entry_data in master_matrix
        ])
        db.session.commit()
        
        return result
    # Function: enrich_item_with_multi_db_data
    @staticmethod
    def enrich_item_with_multi_db_data(item: Any, app_id: str) -> Dict[str, Any]:
        """Enrich an item with data from multiple databases for missing fields.
        
        Strategy: For removed columns from CAST, lookup from IndustryData then CorentData
        
        Args:
            item: The item to enrich (any model)
            app_id: The application ID to lookup
            
        Returns:
            Dictionary with enriched fields including application_type and capabilities
        """
        enriched = {}
        
        # Start with direct attributes from item
        if hasattr(item, '__dict__'):
            enriched = {k: v for k, v in item.__dict__.items() if not k.startswith('_')}
        elif isinstance(item, dict):
            enriched = item.copy()
        
        # Try to get application_type and capabilities from IndustryData first
        try:
            industry_item = IndustryData.query.filter_by(app_id=app_id).first()
            if industry_item:
                enriched['application_type'] = getattr(industry_item, 'application_type', None) or enriched.get('application_type')
                enriched['capabilities'] = getattr(industry_item, 'capabilities', None) or enriched.get('capabilities')
                return enriched
        except Exception:
            pass
        
        # Fall back to CorentData
        try:
            corent_item = None  # app_id removed from CorentData, lookup not possible
            if corent_item:
                enriched['application_type'] = getattr(corent_item, 'application_type', None) or enriched.get('application_type')
                enriched['capabilities'] = getattr(corent_item, 'capabilities', None) or enriched.get('capabilities')
                return enriched
        except Exception:
            pass
        
        return enriched