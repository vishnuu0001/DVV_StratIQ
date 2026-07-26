# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Traceability Matrix Service
# Date: 2026-04-06
# ---------------------------------------------------------------------------
"""
Traceability Matrix Service
Generates comprehensive application-to-infrastructure mappings with rationalization actions
"""

import json
import logging
import os
import threading
import time
from pathlib import Path

from app.models.industry_data import IndustryData
from app.models.corent_data import CorentData
from app.models.cast import CASTData

logger = logging.getLogger(__name__)

_CACHE_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "traceability_insights_cache.json"
_LLM_TTL_SECONDS = 7200  # 2 hours

# Function: _load_file_cache
def _load_file_cache():
    try:
        if _CACHE_FILE.exists():
            data = json.loads(_CACHE_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict) and data.get("_ts"):
                return data
    except Exception:
        pass
    return {}

# Function: _save_file_cache
def _save_file_cache(data: dict):
    try:
        _CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        _CACHE_FILE.write_text(json.dumps(data, ensure_ascii=False, default=str), encoding="utf-8")
    except Exception as exc:
        logger.warning("Could not save traceability file cache: %s", exc)


class TraceabilityService:
    """Service for generating traceability matrix with action recommendations"""

    _llm_insights_cache: dict = {}
    _llm_refresh_lock = threading.Lock()
    _llm_refreshing = False

    # Function: _load_industry_apps
    @staticmethod
    def _load_industry_apps():
        """Fetch all applications, falling back to the correlation workspace when IndustryData is empty."""
        from app import db

        industry_apps = db.session.query(
            IndustryData.app_id,
            IndustryData.app_name,
            IndustryData.platform_host,
            IndustryData.application_type,
            IndustryData.capabilities
        ).all()

        if industry_apps:
            return industry_apps

        try:
            from app.models.correlation_workspace import WorkspaceBizRow, WorkspaceRun
            latest_run = WorkspaceRun.query.filter_by(status='done').order_by(WorkspaceRun.id.desc()).first()
            if latest_run:
                industry_apps = WorkspaceBizRow.query.filter_by(run_id=latest_run.id).all()
        except Exception as exc:
            logger.warning("Workspace fallback for traceability failed: %s", exc)

        return industry_apps

    # Function: _build_capability_groups
    @staticmethod
    def _build_capability_groups(industry_apps):
        """Build capability -> [app_id, ...] groups, used to determine redundancy."""
        capability_groups = {}
        for app in industry_apps:
            if not app.capabilities:
                continue
            caps = [c.strip() for c in str(app.capabilities).split(',') if c.strip()]
            for cap in caps:
                if cap not in capability_groups:
                    capability_groups[cap] = []
                capability_groups[cap].append(app.app_id)
        return capability_groups

    # Function: _redundancy_and_action
    @staticmethod
    def _redundancy_and_action(apps_with_cap):
        """Determine redundancy level + recommended action for a capability's app count."""
        if apps_with_cap == 1:
            return 'Unique', 'Retain'
        if apps_with_cap == 2:
            return 'Duplicate', 'Migrate to SAP'
        action = 'Decommission' if apps_with_cap > 3 else 'Migrate to SAP'
        return 'High', action

    # Function: _traceability_entries_for_app
    @staticmethod
    def _traceability_entries_for_app(app, cast_data, capability_groups):
        """Build the traceability_matrix row(s) for one application."""
        infrastructure = app.platform_host or 'Unknown'
        cast_item = cast_data.get(app.app_id)
        repository = f"repo/{app.app_id}" if cast_item else 'N/A'

        if not app.capabilities:
            return [{
                'app_id': app.app_id,
                'infrastructure': infrastructure,
                'application': app.app_name,
                'repository': repository,
                'capability': 'Unclassified',
                'application_type': app.application_type or 'Unknown',
                'redundancy': 'Unique',
                'action': 'Retain',
                'apps_with_capability': 1
            }]

        caps = [c.strip() for c in str(app.capabilities).split(',') if c.strip()]
        entries = []
        for capability in caps:
            apps_with_cap = len(capability_groups.get(capability, []))
            redundancy, action = TraceabilityService._redundancy_and_action(apps_with_cap)
            entries.append({
                'app_id': app.app_id,
                'infrastructure': infrastructure,
                'application': app.app_name,
                'repository': repository,
                'capability': capability,
                'application_type': app.application_type or 'Unknown',
                'redundancy': redundancy,
                'action': action,
                'apps_with_capability': apps_with_cap
            })
        return entries

    # Function: _compute_traceability_summary
    @staticmethod
    def _compute_traceability_summary(industry_apps, traceability_matrix):
        """Single-pass summary statistics. Each app is assigned its most severe
        action (Decommission > Migrate to SAP > Retain)."""
        action_priority = {'Decommission': 3, 'Migrate to SAP': 2, 'Retain': 1}
        app_dominant_action = {}  # app_id -> dominant action
        infra_set = set()
        cap_set = set()
        dup_app_ids = set()
        for item in traceability_matrix:
            act = item['action']
            aid = item['app_id']
            if action_priority.get(act, 0) > action_priority.get(app_dominant_action.get(aid, ''), 0):
                app_dominant_action[aid] = act
            infra_set.add(item['infrastructure'])
            cap_set.add(item['capability'])
            if item['redundancy'] in ('Duplicate', 'High'):
                dup_app_ids.add(item['app_id'])

        retain_count      = sum(1 for a in app_dominant_action.values() if a == 'Retain')
        migrate_count     = sum(1 for a in app_dominant_action.values() if a == 'Migrate to SAP')
        decommission_count = sum(1 for a in app_dominant_action.values() if a == 'Decommission')

        potential_consolidation = len(dup_app_ids)
        unique_capabilities = len(cap_set)

        return {
            'total_applications': len(industry_apps),
            'total_entries': len(traceability_matrix),
            'unique_infrastructure': len(infra_set),
            'unique_capabilities': unique_capabilities,
            'applications_to_retain': retain_count,
            'applications_to_migrate': migrate_count,
            'applications_to_decommission': decommission_count,
            'potential_consolidation': potential_consolidation,
            'consolidation_ratio': f"{potential_consolidation}:{unique_capabilities}"
        }

    # Function: _attach_llm_insights
    @staticmethod
    def _attach_llm_insights(result, summary, traceability_matrix):
        """Stale-while-revalidate LLM insights cache (mutates result['llm_insights'] in
        place) and kicks off a background refresh thread when the cache is stale/absent."""
        now = time.time()

        # L1: in-memory cache
        mem = TraceabilityService._llm_insights_cache
        if mem and (now - mem.get('_ts', 0)) < _LLM_TTL_SECONDS:
            result['llm_insights'] = {k: v for k, v in mem.items() if k != '_ts'}
            return

        # L2: file cache
        file_cache = _load_file_cache()
        cache_age = now - file_cache.get('_ts', 0)
        if file_cache and cache_age < _LLM_TTL_SECONDS:
            # Fresh enough — promote to memory
            TraceabilityService._llm_insights_cache = file_cache
            result['llm_insights'] = {k: v for k, v in file_cache.items() if k != '_ts'}
            return

        # ── Cache is stale or absent ────────────────────────────────────────
        # Return stale data immediately (or available=false) while refreshing in background.
        if file_cache:
            result['llm_insights'] = {k: v for k, v in file_cache.items() if k != '_ts'}
        else:
            result['llm_insights'] = {'available': False, 'status': 'generating'}

        # Function: _background_refresh
        def _background_refresh(summary_snapshot, matrix_snapshot):
            with TraceabilityService._llm_refresh_lock:
                if TraceabilityService._llm_refreshing:
                    return
                TraceabilityService._llm_refreshing = True
            try:
                from app.services.ollama_service import OllamaService
                sample = sorted(
                    matrix_snapshot,
                    key=lambda x: {'High': 0, 'Duplicate': 1, 'Unique': 2}.get(x.get('redundancy', 'Unique'), 3)
                )[:20]
                insights = OllamaService.generate_traceability_insights(summary_snapshot, sample)
                if insights.get('available'):
                    insights['_ts'] = time.time()
                    TraceabilityService._llm_insights_cache = insights
                    _save_file_cache(insights)
                    logger.info("Traceability LLM insights refreshed and cached.")
            except Exception as exc:
                logger.warning("Background traceability LLM refresh failed: %s", exc)
            finally:
                TraceabilityService._llm_refreshing = False

        t = threading.Thread(
            target=_background_refresh,
            args=(summary, list(traceability_matrix)),
            daemon=True,
        )
        t.start()

    # Function: get_traceability_matrix
    @staticmethod
    def get_traceability_matrix():
        """
        Generate complete traceability matrix with all 195 applications
        mapped to infrastructure, repositories, and capabilities

        Returns:
            dict with traceability data and summary statistics
        """
        from app import db

        industry_apps = TraceabilityService._load_industry_apps()

        # Get CAST data for repositories
        cast_data = {item.app_id: item for item in db.session.query(CASTData).all()}

        # Get CorentData for additional infrastructure info
        corent_data = {}  # app_id/app_name removed from CorentData

        # Build capability groups to determine redundancy
        capability_groups = TraceabilityService._build_capability_groups(industry_apps)

        # Generate traceability entries
        traceability_matrix = []
        for app in industry_apps:
            traceability_matrix.extend(
                TraceabilityService._traceability_entries_for_app(app, cast_data, capability_groups)
            )

        summary = TraceabilityService._compute_traceability_summary(industry_apps, traceability_matrix)

        result = {
            'matrix': traceability_matrix,
            'summary': summary,
        }

        TraceabilityService._attach_llm_insights(result, summary, traceability_matrix)

        return result
