# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Business Capability Mapping Service
# Date: 2026-05-05
# ---------------------------------------------------------------------------
"""
Business Capability Mapping Service
Joins CORENT and CAST data to create capability-based application mappings
"""

import json
import logging
import os
import time
from sqlalchemy import func, and_
from app.models.corent_data import CorentData
from app.models.cast import ApplicationClassification, CASTData
from app.models.industry_data import IndustryData

logger = logging.getLogger(__name__)

# Persistent file-based LLM cache (survives Flask restarts)
_CACHE_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'capability_insights_cache.json')
_CACHE_TTL = 7200  # 2 hours


# Function: _load_file_cache
def _load_file_cache() -> dict:
    try:
        if os.path.exists(_CACHE_FILE):
            with open(_CACHE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if time.time() - data.get('_ts', 0) < _CACHE_TTL:
                return data
    except Exception:
        pass
    return {}


# Function: _save_file_cache
def _save_file_cache(data: dict) -> None:
    try:
        os.makedirs(os.path.dirname(_CACHE_FILE), exist_ok=True)
        with open(_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f)
    except Exception as exc:
        logger.warning("Could not save capability cache: %s", exc)


class BusinessCapabilityService:
    """Service for creating and analyzing business capability mappings"""

    _llm_insights_cache: dict = {}

    # Function: _get_capability_llm_insights
    @staticmethod
    def _get_capability_llm_insights(capability_summary_for_llm: dict) -> dict:
        """Return LLM capability insights using in-memory → file → live LLM cascade."""
        from app.services.ollama_service import OllamaService
        _now = time.time()
        _mem = BusinessCapabilityService._llm_insights_cache
        if _mem and _mem.get('available') and (_now - _mem.get('_ts', 0)) < _CACHE_TTL:
            return {k: v for k, v in _mem.items() if k != '_ts'}
        _file_cached = _load_file_cache()
        if _file_cached and _file_cached.get('available'):
            BusinessCapabilityService._llm_insights_cache = _file_cached
            return {k: v for k, v in _file_cached.items() if k != '_ts'}
        llm_insights = OllamaService.generate_capability_insights(capability_summary_for_llm)
        llm_insights['_ts'] = _now
        BusinessCapabilityService._llm_insights_cache = llm_insights
        if llm_insights.get('available'):
            _save_file_cache(llm_insights)
        return {k: v for k, v in llm_insights.items() if k != '_ts'}

    # Function: _map_app_row_to_dict
    @staticmethod
    def _map_app_row_to_dict(item):
        """Map an IndustryData or WorkspaceBizRow item to the app mapping dict (same attrs on both)."""
        return {
            'app_id': item.app_id,
            'app_name': item.app_name,
            'business_owner': item.business_owner or 'Unknown',
            'architecture_type': item.architecture_type or 'N/A',
            'platform_host': item.platform_host or 'N/A',
            'application_type': item.application_type or 'N/A',
            'install_type': item.install_type or 'N/A',
            'capability': item.capabilities or 'Unclassified',
        }

    # Function: _map_corent_row_to_dict
    @staticmethod
    def _map_corent_row_to_dict(corent_app):
        return {
            'app_id': str(corent_app.id),
            'app_name': 'N/A',
            'business_owner': corent_app.business_owner or 'Unknown',
            'architecture_type': corent_app.architecture_type or 'N/A',
            'platform_host': corent_app.platform_host or 'N/A',
            'application_type': 'N/A',
            'install_type': corent_app.install_type or 'N/A',
            'capability': 'Unclassified',
        }

    # Function: _build_pagination_meta
    @staticmethod
    def _build_pagination_meta(page, per_page, total_count):
        pages = (total_count + per_page - 1) // per_page
        return {
            'page': page,
            'per_page': per_page,
            'total': total_count,
            'pages': pages,
            'has_next': page < pages,
            'has_prev': page > 1,
        }

    # Function: _paginate_workspace_biz_rows
    @staticmethod
    def _paginate_workspace_biz_rows(page, per_page):
        """Return a paginated mapping dict from the latest WorkspaceBizRow run, or None if unavailable."""
        from app.models.correlation_workspace import WorkspaceBizRow, WorkspaceRun
        latest_run = WorkspaceRun.query.filter_by(status='done').order_by(WorkspaceRun.id.desc()).first()
        if not latest_run:
            return None
        query = WorkspaceBizRow.query.filter_by(run_id=latest_run.id).order_by(WorkspaceBizRow.app_name)
        total_count = query.count()
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        applications = [BusinessCapabilityService._map_app_row_to_dict(item) for item in paginated.items]
        return {
            'applications': applications,
            'pagination': BusinessCapabilityService._build_pagination_meta(page, per_page, total_count),
        }

    # Function: get_capability_application_mapping
    @staticmethod
    def get_capability_application_mapping(page=1, per_page=10):
        """
        Get paginated application-to-capability mappings

        Args:
            page: Page number (1-indexed)
            per_page: Applications per page

        Returns:
            dict with paginated data and metadata
        """
        from app import db
        from sqlalchemy import func

        # Always prefer IndustryData — it has app_id, app_name, application_type and capabilities.
        # Fall back to CorentData only when IndustryData has no records.
        industry_count = db.session.query(func.count(IndustryData.id)).scalar() or 0

        # Further fallback: use workspace_biz_rows when legacy tables are empty
        if industry_count == 0:
            try:
                workspace_result = BusinessCapabilityService._paginate_workspace_biz_rows(page, per_page)
                if workspace_result is not None:
                    return workspace_result
            except Exception:
                pass

        if industry_count > 0:
            industry_query = db.session.query(IndustryData).order_by(IndustryData.app_name)
            total_count = industry_query.count()
            paginated_apps = industry_query.paginate(page=page, per_page=per_page, error_out=False)
            applications = [BusinessCapabilityService._map_app_row_to_dict(item) for item in paginated_apps.items]
        else:
            # Fallback: CorentData only (no application_type/capabilities available)
            corent_query = db.session.query(CorentData).order_by(CorentData.id)
            total_count = corent_query.count()
            paginated_apps = corent_query.paginate(page=page, per_page=per_page, error_out=False)
            applications = [BusinessCapabilityService._map_corent_row_to_dict(a) for a in paginated_apps.items]

        return {
            'applications': applications,
            'pagination': BusinessCapabilityService._build_pagination_meta(page, per_page, total_count),
        }

    # Function: _load_industry_apps_with_fallback
    @staticmethod
    def _load_industry_apps_with_fallback():
        """Query IndustryData apps with capabilities; fall back to WorkspaceBizRow if empty."""
        from app import db
        industry_apps = db.session.query(
            IndustryData.app_id,
            IndustryData.app_name,
            IndustryData.capabilities,
            IndustryData.business_owner,
            IndustryData.application_type
        ).filter(
            IndustryData.capabilities.isnot(None),
            IndustryData.capabilities != ''
        ).all()
        total_portfolio_apps = db.session.query(func.count(IndustryData.id)).scalar() or 0

        if not industry_apps:
            try:
                from app.models.correlation_workspace import WorkspaceBizRow, WorkspaceRun
                latest_run = WorkspaceRun.query.filter_by(status='done').order_by(WorkspaceRun.id.desc()).first()
                if latest_run:
                    total_portfolio_apps = WorkspaceBizRow.query.filter_by(run_id=latest_run.id).count()
                    ws_rows = WorkspaceBizRow.query.filter(
                        WorkspaceBizRow.run_id == latest_run.id,
                        WorkspaceBizRow.capabilities.isnot(None),
                        WorkspaceBizRow.capabilities != ''
                    ).all()
                    industry_apps = ws_rows
            except Exception:
                pass
        return industry_apps, total_portfolio_apps

    # Function: _group_apps_by_capability
    @staticmethod
    def _group_apps_by_capability(industry_apps):
        """Group app dicts by each comma-separated capability value."""
        capability_groups = {}
        for app in industry_apps:
            caps = [c.strip() for c in str(app.capabilities).split(',') if c.strip()]
            for cap in caps:
                if cap not in capability_groups:
                    capability_groups[cap] = []
                capability_groups[cap].append({
                    'app_id': app.app_id,
                    'app_name': app.app_name,
                    'business_owner': app.business_owner or 'Unknown',
                    'application_type': app.application_type or 'N/A'
                })
        return capability_groups

    # Function: _collect_unique_app_ids
    @staticmethod
    def _collect_unique_app_ids(capability_groups):
        unique_app_ids = set()
        for app_list in capability_groups.values():
            for a in app_list:
                if a.get('app_id'):
                    unique_app_ids.add(a['app_id'])
        return unique_app_ids

    # Function: _collect_elimination_candidates
    @staticmethod
    def _collect_elimination_candidates(capability_groups):
        elimination_candidates_count = 0
        redundant_app_ids = set()
        total_consolidation_slots = 0

        for apps in capability_groups.values():
            if len(apps) > 1:
                elimination_candidates_count += 1
                total_consolidation_slots += len(apps) - 1
                for a in apps[1:]:
                    if a.get('app_id'):
                        redundant_app_ids.add(a['app_id'])

        return elimination_candidates_count, redundant_app_ids, total_consolidation_slots

    # Function: _compute_capability_elimination_stats
    @staticmethod
    def _compute_capability_elimination_stats(capability_groups):
        """Scan capability groups and return elimination stats."""
        apps_with_capabilities = len(BusinessCapabilityService._collect_unique_app_ids(capability_groups))
        elimination_candidates_count, redundant_app_ids, total_consolidation_slots = (
            BusinessCapabilityService._collect_elimination_candidates(capability_groups)
        )
        return apps_with_capabilities, elimination_candidates_count, len(redundant_app_ids), total_consolidation_slots

    # Function: get_capability_analysis
    @staticmethod
    def get_capability_analysis():
        """
        Analyze applications grouped by capability to identify elimination candidates.
        Gets capabilities from IndustryData and joins with Corent and CAST data.
        
        Returns:
            dict with capability analysis based on actual Industry/Corent/CAST data
        """
        from app import db

        industry_apps, total_portfolio_apps = BusinessCapabilityService._load_industry_apps_with_fallback()
        capability_groups = BusinessCapabilityService._group_apps_by_capability(industry_apps)

        apps_with_capabilities, elimination_candidates_count, total_redundant_apps, total_consolidation_slots = (
            BusinessCapabilityService._compute_capability_elimination_stats(capability_groups)
        )
        apps_with_capabilities = apps_with_capabilities or len(industry_apps)

        capabilities = []
        for capability, apps in sorted(capability_groups.items(), key=lambda x: len(x[1]), reverse=True):
            app_count = len(apps)
            is_elimination_candidate = app_count > 1

            # Get sample app
            sample_app = apps[0]['app_name'] if apps else 'Unknown'

            # Calculate optimization potential
            optimization_potential = {
                'redundant_apps': max(0, app_count - 1),
                'consolidation_ratio': f'{app_count}:1',
                'target_apps': 1
            }

            cap_obj = {
                'capability': capability,
                'app_count': app_count,
                'is_elimination_candidate': is_elimination_candidate,
                'elimination_reason': f'{app_count} applications provide this capability - consolidation opportunity' if is_elimination_candidate else None,
                'sample_app': sample_app,
                'apps': apps,
                'optimization_potential': optimization_potential,
                'priority': 'HIGH' if app_count > 5 else 'MEDIUM' if app_count > 2 else 'LOW'
            }

            capabilities.append(cap_obj)
        
        result = {
            'summary': {
                'total_capabilities': len(capabilities),
                'total_applications': total_portfolio_apps or apps_with_capabilities,
                'apps_with_capabilities': apps_with_capabilities,
                'elimination_candidates': elimination_candidates_count,
                'total_redundant_apps': total_redundant_apps,
                'total_consolidation_slots': total_consolidation_slots,
                'apps_with_shared_capability': elimination_candidates_count
            },
            'capabilities': capabilities
        }

        # Enrich with LLM insights (file cache → in-memory cache → LLM call)
        try:
            capability_summary_for_llm = {
                'total_capabilities': len(capabilities),
                'total_applications': total_portfolio_apps or apps_with_capabilities,
                'elimination_candidates': elimination_candidates_count,
                'total_redundant_apps': total_redundant_apps,
                'total_consolidation_slots': total_consolidation_slots,
                'top_capabilities': [
                    {
                        'capability': c['capability'],
                        'app_count': c['app_count'],
                        'priority': c['priority'],
                        'is_elimination_candidate': c['is_elimination_candidate'],
                    }
                    for c in capabilities[:20]
                ],
            }
            result['llm_insights'] = BusinessCapabilityService._get_capability_llm_insights(capability_summary_for_llm)
        except Exception as exc:
            logger.warning("Capability LLM insights skipped: %s", exc)
            result['llm_insights'] = {"available": False, "error": str(exc)}

        return result

    # Function: _capability_search_matches
    @staticmethod
    def _capability_search_matches(caps_str, caps_lower, search_term, capability_name):
        return search_term in caps_lower or capability_name.lower() in caps_str.lower()

    # Function: _build_capability_app_entry
    @staticmethod
    def _build_capability_app_entry(app):
        return {
            'app_id': app.app_id,
            'app_name': app.app_name,
            'business_owner': app.business_owner or 'Unknown',
            'architecture_type': app.architecture_type or 'N/A',
            'platform_host': app.platform_host or 'N/A',
            'application_type': app.application_type or 'N/A',
            'install_type': 'N/A',  # app_id removed from CorentData, join not possible
            'technology_stack': app.application_type or 'N/A'
        }

    # Function: _filter_apps_by_capability
    @staticmethod
    def _filter_apps_by_capability(all_apps, capability_name):
        # Normalize the search term: strip "(Provides)"/"(Consumes)" suffixes for flexible matching
        search_term = capability_name.lower().replace(' (provides)', '').replace(' (consumes)', '').strip()
        applications = []
        for app in all_apps:
            caps_str = str(app.capabilities) if app.capabilities else ""
            caps_lower = caps_str.lower().replace(' (provides)', '').replace(' (consumes)', '')
            if BusinessCapabilityService._capability_search_matches(caps_str, caps_lower, search_term, capability_name):
                applications.append(BusinessCapabilityService._build_capability_app_entry(app))
        return applications

    # Function: _group_apps_by_tech_stack
    @staticmethod
    def _group_apps_by_tech_stack(applications):
        tech_stacks = {}
        for app_dict in applications:
            tech = app_dict['technology_stack']
            if tech not in tech_stacks:
                tech_stacks[tech] = []
            tech_stacks[tech].append(app_dict['app_name'])
        return tech_stacks

    # Function: _build_capability_consolidation_analysis
    @staticmethod
    def _build_capability_consolidation_analysis(applications):
        if len(applications) > 1:
            tech_stacks = BusinessCapabilityService._group_apps_by_tech_stack(applications)
            apps_to_consolidate = len(applications)
            apps_to_eliminate = max(1, apps_to_consolidate - 1)
            return {
                'total_apps': len(applications),
                'is_elimination_candidate': True,
                'elimination_reason': f'{len(applications)} applications provide this capability',
                'technology_distribution': tech_stacks,
                'consolidation_summary': {
                    'apps_to_consolidate': apps_to_consolidate,
                    'apps_to_eliminate': apps_to_eliminate,
                    'consolidation_ratio': f'{apps_to_consolidate}:1',
                    'recommendation': f'Consolidate {apps_to_consolidate} applications into 1 optimal solution, eliminate {apps_to_eliminate} redundant applications'
                }
            }
        return {
            'total_apps': len(applications),
            'is_elimination_candidate': False,
            'elimination_reason': None,
            'recommendation': 'Single application - already optimal. No consolidation needed.' if len(applications) == 1 else 'No applications found for this capability.'
        }

    # Function: get_capability_details
    @staticmethod
    def get_capability_details(capability_name):
        """
        Get all applications for a specific capability with consolidation analysis

        Args:
            capability_name: Name of the business capability

        Returns:
            dict with capability details and applications (actual data only)
        """
        from app import db

        # Query ALL industry apps (no filtering initially)
        ALL_apps = db.session.query(IndustryData).filter(
            IndustryData.capabilities.isnot(None),
            IndustryData.capabilities != ''
        ).all()

        applications = BusinessCapabilityService._filter_apps_by_capability(ALL_apps, capability_name)
        analysis = BusinessCapabilityService._build_capability_consolidation_analysis(applications)

        return {
            'capability': capability_name,
            'analysis': analysis,
            'applications': applications
        }

    # Function: get_capability_mapping_export
    @staticmethod
    def get_capability_mapping_export(format_type='json'):
        """
        Export complete capability mapping for analysis
        
        Args:
            format_type: Export format ('json', 'csv')
            
        Returns:
            dict with exportable data
        """
        from app import db
        
# Get complete mapping from CorentData (app_id/app_name removed, no join possible)
        query = db.session.query(
            CorentData.id,
            CorentData.business_owner,
            CorentData.architecture_type,
            CorentData.platform_host,
            CorentData.install_type,
        ).order_by(
            CorentData.id
        ).all()

        data = []
        for app in query:
            data.append({
                'APP_ID': str(app.id),
                'APP_NAME': 'N/A',
                'BUSINESS_OWNER': app.business_owner or 'Unknown',
                'ARCHITECTURE_TYPE': app.architecture_type or 'N/A',
                'PLATFORM_HOST': app.platform_host or 'N/A',
                'APPLICATION_TYPE': 'N/A',
                'INSTALL_TYPE': app.install_type or 'N/A',
                'BUSINESS_CAPABILITY': 'Unclassified'
            })
        
        return {
            'format': format_type,
            'total_records': len(data),
            'data': data
        }
