# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: AppRationalization — backend/app/routes (correlation_bp.py)
# Date: 2026-06-02
# ---------------------------------------------------------------------------
from flask import Blueprint, request, jsonify
from flask import current_app
from flask_cors import cross_origin
from app.services.correlation_service import CorrelationService
from app.services.consolidated_data_service import ConsolidatedDataService
from app.services.ollama_service import OllamaService
from app.models.correlation import CorrelationResult, MasterMatrixEntry
from app import db
import threading as _threading
import uuid as _uuid
import time as _time

correlation_bp = Blueprint('correlation', __name__, url_prefix='/api/correlation')

# ---------------------------------------------------------------------------
# In-process async job tracker — avoids Cloudflare's 100s proxy timeout.
# Only one correlation job runs at a time; subsequent /start calls return the
# running job_id immediately without starting a duplicate.
# ---------------------------------------------------------------------------
_job_lock = _threading.Lock()
_current_job: dict = {}  # {id, step, status, result, error, started}


# Function: _merge_workspace_stats_into_correlation
def _merge_workspace_stats_into_correlation(correlation_data, workspace_result):
    """
    Overwrite correlation_data statistics with the just-completed workspace pipeline's
    counts. The workspace pipeline (ExcelPredictionService) is the one actually
    triggered by "Correlate Files & Start Analysis" and reads the current source
    files directly — it is always the authoritative, freshly-computed result for
    this run. The legacy CorrelationService.correlate_data() call right before this
    only exists for its dashboard/master-matrix side effects and reads from separate
    DB tables (IndustryData/CorentData/CASTData) that are populated by a different,
    older upload flow; those tables can hold stale nonzero counts left over from an
    unrelated previous session. Previously this only overwrote when the legacy stats'
    total_matched was falsy, so any stale-but-nonzero legacy count silently won and
    the Overview tab showed numbers unrelated to the run that had just completed —
    this is the fix for that "wrong counts" behavior. Always prefer workspace numbers
    when the workspace pipeline actually produced a result.
    """
    if not workspace_result.get('status') == 'done':
        return
    ws_stats = correlation_data.get('statistics', {})
    matched_count = workspace_result.get('matched_count', 0)
    cast_rows     = workspace_result.get('cast_rows', 0)
    ws_stats['total_matched']    = matched_count
    ws_stats['correlated_total'] = matched_count
    ws_stats['match_percentage'] = workspace_result.get('match_pct', 0.0)
    ws_stats['cast_total']       = cast_rows
    ws_stats['corent_total']     = workspace_result.get('corent_rows', 0)
    ws_stats['industry_total']   = workspace_result.get('biz_rows', 0)
    ws_stats['match_denom']      = max(cast_rows, 1)

    # Replace the per-phase match breakdown too — leaving direct_matched/
    # server_name_matched/exact_name_matched/fuzzy_matched/unmatched_*_count at their
    # legacy correlate_data() values (computed from separate, unrelated IndustryData/
    # CorentData/CASTData tables) produced self-contradictory output like
    # total_matched=195 alongside unmatched_corent_count=195 in the very same
    # statistics dict. WorkspaceCorrelation already has the real, run-specific
    # breakdown (three_way / cast_biz / cast_corent / unmatched) — use it directly
    # instead of leaving stale numbers from an unrelated dataset next to fresh ones.
    run_id = workspace_result.get('run_id')
    breakdown = {'three_way': 0, 'cast_biz': 0, 'cast_corent': 0, 'unmatched': 0}
    if run_id is not None:
        try:
            from app.models.correlation_workspace import WorkspaceCorrelation
            from sqlalchemy import func as _func
            rows = (
                db.session.query(WorkspaceCorrelation.match_type, _func.count(WorkspaceCorrelation.id))
                .filter_by(run_id=run_id)
                .group_by(WorkspaceCorrelation.match_type)
                .all()
            )
            for match_type, count in rows:
                if match_type in breakdown:
                    breakdown[match_type] = count
        except Exception:
            pass

    ws_stats['direct_matched']      = breakdown['three_way']
    ws_stats['server_name_matched'] = breakdown['cast_corent']
    ws_stats['exact_name_matched']  = breakdown['cast_biz']
    ws_stats['fuzzy_matched']       = 0
    ws_stats['unmatched_cast_count']   = breakdown['unmatched']
    ws_stats['unmatched_corent_count'] = max(cast_rows - matched_count, 0)
    correlation_data['statistics'] = ws_stats


# Function: _build_correlation_job_payload
def _build_correlation_job_payload(
    correlation_id, result_matched_count, result_total_count,
    result_match_percentage, result_created_at,
    correlation_data, workspace_result, pipeline_result,
):
    return {
        'status': 'success',
        'message': 'Correlation and AI analysis completed successfully',
        'correlation_id': correlation_id,
        'summary': {
            'matched_count':    result_matched_count or workspace_result.get('matched_count', 0),
            'total_count':      result_total_count   or workspace_result.get('cast_rows', 0),
            'match_percentage': result_match_percentage or workspace_result.get('match_pct', 0.0),
        },
        'statistics':  correlation_data.get('statistics', {}),
        'timestamp':   result_created_at,
        'workspace':   workspace_result,
        'pipeline': {
            **pipeline_result.get('pipeline_stats', {}),
            'total_ai_fills':    workspace_result.get('cells_predicted', {}).get('total', 0),
            'apps_with_ai_fill': workspace_result.get('apps_with_ai_fill', 0),
            'llm_model':         workspace_result.get('llm_model'),
        },
        'llm_analysis':       pipeline_result.get('llm_analysis', {}),
        'llm_analysis_id':    pipeline_result.get('llm_analysis_id'),
        'consolidated_count': pipeline_result.get('consolidated_count', 0),
    }


# Function: _update_analysis_row_fields
def _update_analysis_row_fields(analysis_row, llm_analysis, consolidated_count):
    from sqlalchemy.orm.attributes import flag_modified
    analysis_row.model_used               = llm_analysis.get('model_used', OllamaService.get_selected_model())
    analysis_row.analysis_type            = 'deep'
    analysis_row.executive_summary        = llm_analysis.get('summary', '')
    analysis_row.cloud_readiness_insight  = llm_analysis.get('cloud_readiness', '')
    analysis_row.risk_observations        = llm_analysis.get('risk_observations', [])
    analysis_row.recommendations          = llm_analysis.get('recommendations', [])
    analysis_row.correlation_quality      = llm_analysis.get('correlation_quality', '')
    analysis_row.per_app_notes            = llm_analysis.get('per_app_notes', {})
    analysis_row.migration_roadmap        = llm_analysis.get('migration_roadmap', [])
    analysis_row.technical_debt_summary   = llm_analysis.get('technical_debt_summary', '')
    analysis_row.modernization_priorities = llm_analysis.get('modernization_priorities', [])
    analysis_row.full_analysis            = llm_analysis
    analysis_row.total_apps_analyzed      = consolidated_count
    for _col in ('risk_observations', 'recommendations', 'per_app_notes',
                 'migration_roadmap', 'modernization_priorities', 'full_analysis'):
        flag_modified(analysis_row, _col)


# ---------------------------------------------------------------------------
# Helper: build corent_dashboard from WorkspaceCorentRow (latest run)
# ---------------------------------------------------------------------------

# Function: _build_corent_dashboard_from_workspace
def _build_corent_dashboard_from_workspace():
    """
    Build the corent_dashboard dict from WorkspaceCorentRow for the latest
    completed workspace run.  Returns None if no workspace data exists yet.

    This avoids the duplicate-count problem caused by combining IndustryData
    (application-level, 195 rows) + CorentData (server-level, 195 rows) which
    produces 390 total entries instead of 195.  WorkspaceCorentRow is loaded
    directly from the CORENT Excel sheet — one row per app, deduplicated by
    app_id — so Tech Stack, Deployment Footprint, etc. are also correct.
    """
    from app.models.correlation_workspace import WorkspaceCorentRow, WorkspaceRun

    latest_run = (
        WorkspaceRun.query
        .filter_by(status='done')
        .order_by(WorkspaceRun.id.desc())
        .first()
    )
    if not latest_run:
        return None

    rows = WorkspaceCorentRow.query.filter_by(run_id=latest_run.id).all()
    if not rows:
        return None

    unique_rows = _deduplicate_corent_rows(rows)
    server_app_mapping, tech_stack, deployment_footprint, server_list = (
        _aggregate_corent_rows(unique_rows)
    )

    return {
        "source":              "WorkspaceCorentRow",
        "server_app_mapping":  server_app_mapping,
        "tech_stack":          tech_stack,
        "deployment_footprint": deployment_footprint,
        "server_list":         list(server_list),
        "total_items":         len(unique_rows),
    }


# Function: _deduplicate_corent_rows
def _deduplicate_corent_rows(rows):
    seen = {}
    for r in rows:
        key = r.app_id if r.app_id else f"__row_{r.source_row_index}"
        if key not in seen or r.last_updated == 'Yes':
            seen[key] = r
    return list(seen.values())


# Function: _aggregate_corent_rows
def _aggregate_corent_rows(unique_rows):
    server_app_mapping = []
    tech_stack = {}
    deployment_footprint = {}
    server_list = set()

    for r in unique_rows:
        tech = r.operating_system
        if tech:
            tech_stack[tech] = tech_stack.get(tech, 0) + 1

        dep = r.deployment_geography or r.environment
        if dep:
            deployment_footprint[dep] = deployment_footprint.get(dep, 0) + 1

        if r.platform_host:
            server_list.add(r.platform_host)

        server_app_mapping.append({
            "app_id":            r.app_id,
            "app_name":          r.app_name,
            "architecture_type": r.architecture_type,
            "business_owner":    r.business_owner,
            "platform_host":     r.platform_host,
            "server_type":       r.server_type,
            "operating_system":  r.operating_system,
            "environment":       r.environment,
            "cloud_suitability": r.cloud_suitability,
            "installed_tech":    r.operating_system or r.db_engine,
            "server":            r.platform_host or "Unknown",
            "last_updated":      r.last_updated,
        })

    return server_app_mapping, tech_stack, deployment_footprint, server_list


# Function: start_correlation
@correlation_bp.route('/start', methods=['POST'])
@cross_origin()
def start_correlation():
    """
    Kick off the full correlation pipeline in a background thread and return
    immediately so the response completes well under Cloudflare's 100s proxy
    timeout.  The caller should poll GET /api/correlation/job-status to track
    progress and retrieve results when status == 'done'.
    """
    global _current_job

    with _job_lock:
        # If a job is already running, return its ID so the caller can poll it.
        if _current_job.get('status') == 'running':
            return jsonify({
                'status': 'running',
                'job_id': _current_job['id'],
                'step':   _current_job.get('step', 'copy'),
                'message': 'Correlation already in progress.',
            }), 202

        job_id = str(_uuid.uuid4())
        _current_job = {
            'id':      job_id,
            'step':    'copy',
            'status':  'running',
            'result':  None,
            'error':   None,
            'started': _time.time(),
        }

    app_ctx = current_app._get_current_object()

    # Function: _run
    def _run():
        global _current_job
        try:
            with app_ctx.app_context():
                # Step 0 — workspace / Excel pipeline
                from app.services.excel_prediction_service import ExcelPredictionService
                _current_job['step'] = 'copy'
                workspace_result = ExcelPredictionService.run_workspace_pipeline(app=app_ctx)
                if workspace_result.get('status') != 'done':
                    with _job_lock:
                        _current_job['status'] = 'error'
                        _current_job['error']  = 'Workspace pipeline failed before correlation'
                    return

                # Step A — standard correlation
                _current_job['step'] = 'correlate'
                correlation_data = CorrelationService.correlate_data()
                ws_corent_dash = _build_corent_dashboard_from_workspace()
                if ws_corent_dash:
                    correlation_data['corent_dashboard'] = ws_corent_dash

                _merge_workspace_stats_into_correlation(correlation_data, workspace_result)

                result = CorrelationService.create_correlation_result(correlation_data)
                # Snapshot scalar values now to avoid accessing an ORM instance
                # after later commits/rollbacks in downstream pipeline steps.
                correlation_id = result.id
                result_matched_count = result.matched_count
                result_total_count = result.total_count
                result_match_percentage = result.match_percentage
                result_created_at = result.created_at.isoformat() if result.created_at else None

                # Step B — null prediction + consolidation + LLM
                _current_job['step'] = 'predict'
                pipeline_result = ConsolidatedDataService.run_full_pipeline(
                    correlation_data=correlation_data,
                    correlation_result_id=correlation_id,
                    run_llm_annotation=False,
                )
                _current_job['step'] = 'analyse'

                payload = _build_correlation_job_payload(
                    correlation_id,
                    result_matched_count,
                    result_total_count,
                    result_match_percentage,
                    result_created_at,
                    correlation_data,
                    workspace_result,
                    pipeline_result,
                )

                with _job_lock:
                    _current_job['status'] = 'done'
                    _current_job['result'] = payload

        except Exception as exc:
            # app_ctx.logger, not current_app.logger — the `with app_ctx.app_context()`
            # block above has already been exited by the time this except clause
            # runs, so current_app's context-local proxy would raise "working
            # outside of application context" here.
            app_ctx.logger.exception("Correlation pipeline job failed")
            with _job_lock:
                _current_job['status'] = 'error'
                _current_job['error']  = str(exc)

    t = _threading.Thread(target=_run, daemon=True)
    t.start()

    return jsonify({
        'status':  'started',
        'job_id':  job_id,
        'step':    'copy',
        'message': 'Correlation pipeline started. Poll /api/correlation/job-status for progress.',
    }), 202


# Function: get_job_status
@correlation_bp.route('/job-status', methods=['GET'])
@cross_origin()
def get_job_status():
    """
    Return the status of the currently running (or last completed) correlation job.
    Poll this endpoint every 3-5 s after calling POST /start.

    Response fields:
      status  — 'idle' | 'running' | 'done' | 'error'
      step    — current pipeline step name (copy / predict / consolidate / correlate / analyse)
      job_id  — job identifier returned by /start
      result  — full correlation payload (only when status == 'done')
      error   — error message (only when status == 'error')
      elapsed — seconds since job started
    """
    with _job_lock:
        job = dict(_current_job)

    if not job:
        return jsonify({'status': 'idle'}), 200

    resp = {
        'status':  job.get('status', 'idle'),
        'step':    job.get('step'),
        'job_id':  job.get('id'),
        'elapsed': round(_time.time() - job.get('started', _time.time()), 1),
    }
    if job.get('status') == 'done':
        resp['result'] = job.get('result')
    if job.get('status') == 'error':
        resp['error'] = job.get('error', 'Unknown error')
    return jsonify(resp), 200



# Function: get_latest_correlation
@correlation_bp.route('/latest', methods=['GET'])
@cross_origin()
def get_latest_correlation():
    """
    Get the latest correlation result with full data.
    
    Returns:
        JSON with complete correlation data and master matrix
    """
    try:
        # Get latest correlation result
        result = CorrelationResult.query.order_by(CorrelationResult.created_at.desc()).first()
        
        if not result:
            return jsonify({
                'status': 'empty',
                'message': 'No correlation results found. Run correlation first.',
                'correlation': None,
                'corent_dashboard': {
                    'server_app_mapping': [],
                    'tech_stack': {},
                    'deployment_footprint': {},
                    'total_applications': 0,
                    'total_servers': 0
                },
                'cast_dashboard': {
                    'repo_app_mapping': [],
                    'architecture_components': [],
                    'internal_dependencies': {},
                    'total_applications': 0,
                    'total_components': 0
                },
                'correlation_layer': [],
                'unmatched_corent': [],
                'unmatched_cast': [],
                'master_matrix': [],
                'statistics': {}
            }), 200
        
        import json

        correlation_data = json.loads(result.correlation_data) if isinstance(result.correlation_data, str) else result.correlation_data

        # Use workspace CORENT data when available (correct count, tech stack, footprint)
        ws_corent_dash = _build_corent_dashboard_from_workspace()
        corent_dash = ws_corent_dash or correlation_data.get('corent_dashboard', {})
        cast_dash   = correlation_data.get('cast_dashboard', {})
        stored_matrix = json.loads(result.master_matrix) if isinstance(result.master_matrix, str) else (result.master_matrix or [])

        return jsonify({
            'status': 'success',
            'correlation': {
                'id': result.id,
                'created_at': result.created_at.isoformat(),
                'matched_count': result.matched_count,
                'total_count': result.total_count,
                'match_percentage': result.match_percentage,
            },
            'corent_dashboard': {
                'server_app_mapping': corent_dash.get('server_app_mapping', []),
                'tech_stack': corent_dash.get('tech_stack', {}),
                'deployment_footprint': corent_dash.get('deployment_footprint', {}),
                'total_applications': corent_dash.get('total_items') or len(
                    {a.get('app_id') or a.get('app_name') for a in corent_dash.get('server_app_mapping', []) if a.get('app_id') or a.get('app_name')}
                ) or len(corent_dash.get('server_app_mapping', [])),
                'total_servers': len(corent_dash.get('server_list', [])),
            },
            'cast_dashboard': {
                'repo_app_mapping': cast_dash.get('repo_app_mapping', []),
                'architecture_components': cast_dash.get('architecture_components', []),
                'internal_dependencies': cast_dash.get('internal_dependencies', {}),
                'total_applications': cast_dash.get('total_items', 0),
                'total_components': len(cast_dash.get('architecture_components', [])),
            },
            'correlation_layer': correlation_data.get('correlation_layer', []),
            'unmatched_corent': correlation_data.get('unmatched_corent', []),
            'unmatched_cast': correlation_data.get('unmatched_cast', []),
            'master_matrix': stored_matrix,
            'statistics': correlation_data.get('statistics', {}),
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to retrieve correlation: {str(e)}'
        }), 500


# Function: get_dashboards
@correlation_bp.route('/dashboards', methods=['GET'])
@cross_origin()
def get_dashboards():
    """
    Get Corent and CAST dashboards separately.
    
    Returns:
        JSON with Corent dashboard (Server-App mapping, Tech stack, Deployment footprint)
        and CAST dashboard (Repo-App mapping, Dependencies, Components)
    """
    try:
        corent_data = CorrelationService.get_corent_data()
        cast_data = CorrelationService.get_cast_data()
        
        return jsonify({
            'status': 'success',
            'corent': {
                'title': 'Infrastructure Discovery',
                'server_app_mapping': corent_data['server_app_mapping'],
                'tech_stack': corent_data['tech_stack'],
                'deployment_footprint': corent_data['deployment_footprint'],
                'total_applications': len(corent_data['server_app_mapping']),
                'total_servers': len(corent_data['server_list'])
            },
            'cast': {
                'title': 'Code Analysis (CAST)',
                'repo_app_mapping': cast_data['repo_app_mapping'],
                'architecture_components': cast_data['architecture_components'],
                'internal_dependencies': cast_data['internal_dependencies'],
                'total_applications': cast_data['total_items'],
                'total_components': len(cast_data['architecture_components'])
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to retrieve dashboards: {str(e)}'
        }), 500


# Function: get_master_matrix
@correlation_bp.route('/master-matrix', methods=['GET'])
@cross_origin()
def get_master_matrix():
    """
    Get the master matrix combining Corent and CAST data.
    
    Query parameters:
        - confidence_level (optional): 'high', 'medium', 'unmatched'
        - limit (optional): Number of rows to return (default: 1000)
        
    Returns:
        JSON with master matrix entries
    """
    try:
        limit = request.args.get('limit', 1000, type=int)
        confidence_level = request.args.get('confidence_level', None)
        
        # Get latest correlation
        result = CorrelationResult.query.order_by(CorrelationResult.created_at.desc()).first()
        
        if not result:
            return jsonify({
                'status': 'not_found',
                'message': 'No correlation results found. Run correlation first.'
            }), 404
        
        import json
        
        master_matrix = json.loads(result.master_matrix) if isinstance(result.master_matrix, str) else result.master_matrix
        
        # Filter by confidence level if specified
        if confidence_level:
            master_matrix = [m for m in master_matrix if m.get('confidence_level') == confidence_level]
        
        # Apply limit
        master_matrix = master_matrix[:limit]
        
        return jsonify({
            'status': 'success',
            'correlation_id': result.id,
            'created_at': result.created_at.isoformat(),
            'total_rows': len(json.loads(result.master_matrix) if isinstance(result.master_matrix, str) else result.master_matrix),
            'returned_rows': len(master_matrix),
            'columns': [
                'Infra',
                'Server',
                'Installed App',
                'App Component',
                'Repo',
                'Confidence'
            ],
            'data': master_matrix
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to retrieve master matrix: {str(e)}'
        }), 500


# Function: get_statistics
@correlation_bp.route('/statistics', methods=['GET'])
@cross_origin()
def get_statistics():
    """
    Get correlation statistics and summary.
    
    Returns:
        JSON with match statistics, unmatched items, confidence distribution
    """
    try:
        result = CorrelationResult.query.order_by(CorrelationResult.created_at.desc()).first()
        
        if not result:
            return jsonify({
                'status': 'not_found',
                'message': 'No correlation results found. Run correlation first.'
            }), 404
        
        import json
        from collections import Counter
        
        correlation_data = json.loads(result.correlation_data) if isinstance(result.correlation_data, str) else result.correlation_data
        
        # Calculate confidence distribution
        confidence_levels = [c.get('confidence_level') for c in correlation_data.get('correlation_layer', [])]
        confidence_dist = dict(Counter(confidence_levels))
        
        # Calculate unmatched percentages
        stored_stats = correlation_data.get('statistics', {})
        corent_total = stored_stats.get('corent_total', 0)
        cast_total = stored_stats.get('cast_total', 0)
        # Support both 'matched_count' and 'total_matched'/'direct_matched' key names
        matched = (stored_stats.get('matched_count') or
                   stored_stats.get('total_matched') or
                   stored_stats.get('direct_matched') or
                   result.matched_count or 0)
        
        unmatched_corent_pct = round((len(correlation_data.get('unmatched_corent', [])) / max(corent_total, 1)) * 100, 2)
        unmatched_cast_pct = round((len(correlation_data.get('unmatched_cast', [])) / max(cast_total, 1)) * 100, 2)
        
        return jsonify({
            'status': 'success',
            'summary': {
                'correlation_id': result.id,
                'created_at': result.created_at.isoformat(),
                'last_updated': result.updated_at.isoformat()
            },
            'statistics': {
                'corent_total': corent_total,
                'cast_total': cast_total,
                'matched_count': matched,
                'match_percentage': round((matched / max(corent_total, 1)) * 100, 2),
                'unmatched_corent': len(correlation_data.get('unmatched_corent', [])),
                'unmatched_corent_percentage': unmatched_corent_pct,
                'unmatched_cast': len(correlation_data.get('unmatched_cast', [])),
                'unmatched_cast_percentage': unmatched_cast_pct
            },
            'confidence_distribution': {
                'high': confidence_dist.get('high', 0),
                'medium': confidence_dist.get('medium', 0),
                'unmatched': confidence_dist.get('unmatched', 0)
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to retrieve statistics: {str(e)}'
        }), 500


# ══════════════════════════════════════════════════════════════════════════
#  Consolidated DB endpoints
# ══════════════════════════════════════════════════════════════════════════

# Function: get_consolidated
@correlation_bp.route('/consolidated', methods=['GET'])
@cross_origin()
def get_consolidated():
    """Return all rows from the consolidated_apps table."""
    try:
        records = ConsolidatedDataService.get_all_consolidated()
        stats = ConsolidatedDataService.get_consolidated_stats()
        return jsonify({
            'status': 'success',
            'count': len(records),
            'stats': stats,
            'records': records,
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# Function: get_consolidated_stats
@correlation_bp.route('/consolidated/stats', methods=['GET'])
@cross_origin()
def get_consolidated_stats():
    """Return aggregate statistics about the consolidated_apps table."""
    try:
        return jsonify({'status': 'success', **ConsolidatedDataService.get_consolidated_stats()}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ── Drill-down: apps grouped by cloud suitability tier ───────────────────────

_HIGH_KW = ('high', 'cloud native', 'cloud-native', 'excellent', 'ready',
            'suitable', 'optimized', 'cloud ready')
_LOW_KW  = ('low', 'unsuitable', 'not suitable', 'poor', 'incompatible',
            'on-premise only', 'on premise')


# Function: _cloud_tier
def _cloud_tier(app) -> str:
    """Compute High / Medium / Low / Unknown cloud-readiness tier for an app."""
    from app.models.consolidated_app import ConsolidatedApp
    cast_v   = (getattr(app, 'cast_cloud_suitability',   None) or '').lower()
    corent_v = (getattr(app, 'corent_cloud_suitability', None) or '').lower()
    if any(k in cast_v for k in _HIGH_KW) or any(k in corent_v for k in _HIGH_KW):
        return 'High'
    if any(k in cast_v for k in _LOW_KW) or any(k in corent_v for k in _LOW_KW):
        return 'Low'
    if cast_v or corent_v:
        return 'Medium'
    return 'Unknown'


# Function: get_apps_by_cloud_group
@correlation_bp.route('/apps/cloud-groups', methods=['GET'])
@cross_origin()
def get_apps_by_cloud_group():
    """
    Return all consolidated apps grouped by computed cloud suitability tier
    (High / Medium / Low / Unknown) for drill-down in the AI Analysis panel.
    """
    try:
        from app.models.consolidated_app import ConsolidatedApp
        apps = ConsolidatedApp.query.order_by(ConsolidatedApp.app_id).all()

        groups: dict = {'High': [], 'Medium': [], 'Low': [], 'Unknown': []}
        for app in apps:
            tier = _cloud_tier(app)
            groups[tier].append({
                'app_id':                        app.app_id,
                'app_name':                      app.app_name,
                'cast_cloud_suitability':        app.cast_cloud_suitability,
                'corent_cloud_suitability':      app.corent_cloud_suitability,
                'cast_application_architecture': app.cast_application_architecture,
                'cast_programming_language':     app.cast_programming_language,
                'cast_component_coupling':       app.cast_component_coupling,
                'corent_platform_host':          app.corent_platform_host,
                'corent_operating_system':       app.corent_operating_system,
                'corent_environment':            app.corent_environment,
                'industry_application_type':     app.industry_application_type,
                'industry_business_owner':       app.industry_business_owner,
                'llm_annotation':                app.llm_annotation,
            })

        return jsonify({
            'status': 'success',
            'groups': groups,
            'counts': {k: len(v) for k, v in groups.items()},
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# Function: get_app_detail
@correlation_bp.route('/apps/<path:app_id>/detail', methods=['GET'])
@cross_origin()
def get_app_detail(app_id):
    """Return full consolidated record for a single app (L3 drill-down)."""
    try:
        from app.models.consolidated_app import ConsolidatedApp
        app = ConsolidatedApp.query.filter_by(app_id=app_id).first()
        if not app:
            return jsonify({'status': 'not_found', 'message': f'App {app_id!r} not found'}), 404
        return jsonify({'status': 'success', 'app': app.to_dict()}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# Function: get_ollama_status
@correlation_bp.route('/ollama/status', methods=['GET'])
@cross_origin()
def get_ollama_status():
    """Check Ollama LLM availability and list installed models."""
    try:
        info = OllamaService.health_info()
        return jsonify({'status': 'success', 'ollama': info}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# Function: get_llm_analysis
@correlation_bp.route('/llm-analysis', methods=['GET'])
@cross_origin()
def get_llm_analysis():
    """
    Return the latest stored deep LLM correlation analysis.

    Includes executive summary, cloud-readiness insights, risk observations,
    recommendations, 3-phase migration roadmap, technical debt summary,
    and modernisation priorities.
    """
    try:
        from app.models.predicted_analysis import LLMCorrelationAnalysis
        from app.models.consolidated_app import ConsolidatedApp

        # Function: _is_stale
        def _is_stale(a) -> bool:
            prios = a.modernization_priorities or []
            if not prios:
                return True
            _PLACEHOLDERS = {"...", "app_id", "<app_id>", "actual_app_id", ""}
            return all(
                str(p.get("app_id", "")).strip().lower() in _PLACEHOLDERS
                or str(p.get("app_id", "")).startswith("<")
                or str(p.get("app_id", "")).startswith("...")
                for p in prios
            )

        analysis = (
            LLMCorrelationAnalysis.query
            .order_by(LLMCorrelationAnalysis.created_at.desc())
            .first()
        )
        if not analysis:
            return jsonify({
                'status': 'not_found',
                'message': 'No LLM analysis found. Run correlation first.',
            }), 404

        # If latest analysis has only placeholder data but real data exists in DB,
        # tell the frontend to prompt for re-run
        has_real_data = ConsolidatedApp.query.count() > 0
        if _is_stale(analysis) and has_real_data:
            return jsonify({
                'status': 'stale',
                'message': 'LLM analysis was generated before data was available. Please re-run the analysis.',
                'total_apps': ConsolidatedApp.query.count(),
            }), 200

        return jsonify({'status': 'success', 'analysis': analysis.to_dict()}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# Function: rerun_llm_analysis
@correlation_bp.route('/llm-analysis/rerun', methods=['POST'])
@cross_origin()
def rerun_llm_analysis():
    """
    Re-run the deep LLM correlation analysis using consolidated data already in DB.
    Updates the latest LLMCorrelationAnalysis row (or creates one if none exists).
    This avoids re-running the full correlation/Excel pipeline.
    """
    import concurrent.futures
    from app.models.predicted_analysis import LLMCorrelationAnalysis
    from app.models.consolidated_app import ConsolidatedApp

    try:
        if not OllamaService.is_available():
            return jsonify({'status': 'error', 'message': 'Ollama is not available.'}), 503

        # Load consolidated records from DB
        consolidated_records = [r.to_dict() for r in ConsolidatedApp.query.all()]
        if not consolidated_records:
            return jsonify({'status': 'error', 'message': 'No consolidated data found. Run correlation first.'}), 404

        stats = ConsolidatedDataService.get_consolidated_stats()
        predictions_summary = {
            'total_fields_predicted': 0,
            'sources_enriched': ['CORENT', 'CAST', 'Industry'],
            'model_used': OllamaService.get_selected_model(),
        }

        # Run with hard timeout — must exceed the inner _generate timeout (180s)
        _TIMEOUT = 220
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
            future = ex.submit(
                OllamaService.generate_deep_correlation_analysis,
                consolidated_records=consolidated_records,
                statistics=stats,
                predictions_summary=predictions_summary,
            )
            try:
                llm_analysis = future.result(timeout=_TIMEOUT)
            except concurrent.futures.TimeoutError:
                future.cancel()
                return jsonify({
                    'status': 'error',
                    'message': f'AI analysis timed out after {_TIMEOUT}s. Try again.',
                }), 504

        if not llm_analysis.get('available'):
            return jsonify({
                'status': 'error',
                'message': llm_analysis.get('error', 'LLM analysis returned no content.'),
            }), 500

        # Update or create the LLMCorrelationAnalysis row
        analysis_row = (
            LLMCorrelationAnalysis.query
            .order_by(LLMCorrelationAnalysis.created_at.desc())
            .first()
        )
        if not analysis_row:
            analysis_row = LLMCorrelationAnalysis()
            db.session.add(analysis_row)

        _update_analysis_row_fields(analysis_row, llm_analysis, len(consolidated_records))

        # flag_modified called inside _update_analysis_row_fields
        db.session.commit()

        return jsonify({'status': 'success', 'analysis': analysis_row.to_dict()}), 200

    except Exception as e:
        current_app.logger.exception("LLM analysis save failed")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# Function: get_predictions
@correlation_bp.route('/predictions', methods=['GET'])
@cross_origin()
def get_predictions():
    """
    Return AI-predicted field-value traceability records.

    Query parameters
    ----------------
    source_category : 'CORENT' | 'CAST' | 'Industry'  (optional filter)
    app_id          : filter by application id         (optional)
    limit           : max rows to return (default 500)
    """
    try:
        from app.models.predicted_analysis import PredictedFieldValue
        from sqlalchemy import func

        source_category = request.args.get('source_category')
        app_id_filter   = request.args.get('app_id')
        limit           = request.args.get('limit', 500, type=int)

        query = PredictedFieldValue.query
        if source_category:
            query = query.filter_by(source_category=source_category)
        if app_id_filter:
            query = query.filter_by(app_id=app_id_filter)

        records = (
            query.order_by(PredictedFieldValue.predicted_at.desc())
            .limit(limit)
            .all()
        )

        # Summary by source
        summary_rows = (
            db.session.query(
                PredictedFieldValue.source_category,
                func.count(PredictedFieldValue.id).label('count'),
            )
            .group_by(PredictedFieldValue.source_category)
            .all()
        )

        return jsonify({
            'status': 'success',
            'total': len(records),
            'summary_by_source': {row.source_category: row.count for row in summary_rows},
            'predictions': [r.to_dict() for r in records],
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ══════════════════════════════════════════════════════════════════════════

# Function: clear_traceability
@correlation_bp.route('/traceability/clear', methods=['DELETE'])
@cross_origin()
def clear_traceability():
    """Clear all correlation results and master matrix entries (resets Traceability page)"""
    try:
        matrix_deleted = MasterMatrixEntry.query.delete()
        results_deleted = CorrelationResult.query.delete()
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Traceability data cleared',
            'deleted': {'correlation_results': results_deleted, 'master_matrix_entries': matrix_deleted}
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


# Function: get_traceability_matrix
@correlation_bp.route('/traceability/matrix', methods=['GET'])
@cross_origin()
def get_traceability_matrix():
    """
    Get complete traceability matrix with all applications mapped to infrastructure,
    capabilities, and recommended rationalization actions.
    
    Returns:
        JSON with full traceability data, summary statistics, and action breakdown
    """
    try:
        from app.services.traceability_service import TraceabilityService
        
        traceability_data = TraceabilityService.get_traceability_matrix()
        
        return jsonify({
            'status': 'success',
            'data': traceability_data['matrix'],
            'summary': traceability_data['summary'],
            'llm_insights': traceability_data.get('llm_insights', {'available': False}),
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to retrieve traceability matrix: {str(e)}'
        }), 500


# ══════════════════════════════════════════════════════════════════════════
#  Workspace endpoints  (new CorrelationWorkspace schema)
# ══════════════════════════════════════════════════════════════════════════

# Function: get_workspace_runs
@correlation_bp.route('/workspace/runs', methods=['GET'])
@cross_origin()
def get_workspace_runs():
    """
    Return all workspace runs in reverse chronological order.

    Query parameters
    ----------------
    limit : int  (default 20)
    """
    try:
        from app.models.correlation_workspace import WorkspaceRun
        limit = request.args.get('limit', 20, type=int)
        runs = (
            WorkspaceRun.query
            .order_by(WorkspaceRun.triggered_at.desc())
            .limit(limit)
            .all()
        )
        return jsonify({
            'status': 'success',
            'count': len(runs),
            'runs': [r.to_dict() for r in runs],
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# Function: get_workspace_run
@correlation_bp.route('/workspace/runs/<int:run_id>', methods=['GET'])
@cross_origin()
def get_workspace_run(run_id):
    """Return a single workspace run detail including aggregated cell-update stats."""
    try:
        from app.models.correlation_workspace import WorkspaceRun, WorkspaceColumnUpdate
        from sqlalchemy import func

        run = db.session.get(WorkspaceRun, run_id)
        if not run:
            return jsonify({'status': 'not_found', 'message': f'Run {run_id} not found'}), 404

        # Per-source predicted-column summary
        summary = (
            db.session.query(
                WorkspaceColumnUpdate.source,
                WorkspaceColumnUpdate.column_name,
                func.count(WorkspaceColumnUpdate.id).label('count'),
            )
            .filter_by(run_id=run_id)
            .group_by(WorkspaceColumnUpdate.source, WorkspaceColumnUpdate.column_name)
            .all()
        )
        by_source: dict = {}
        for row in summary:
            by_source.setdefault(row.source, {})[row.column_name] = row.count

        return jsonify({
            'status': 'success',
            'run': run.to_dict(),
            'predicted_columns_by_source': by_source,
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# Function: get_workspace_cast
@correlation_bp.route('/workspace/cast', methods=['GET'])
@cross_origin()
def get_workspace_cast():
    """
    Return enriched CAST rows for the latest (or specified) workspace run.

    Query parameters
    ----------------
    run_id : int  (default: latest run)
    limit  : int  (default 500)
    """
    try:
        from app.models.correlation_workspace import WorkspaceCastRow, WorkspaceRun
        run_id = request.args.get('run_id', type=int)
        limit  = request.args.get('limit', 500, type=int)

        if run_id is None:
            # status='done' filter is required — an in-progress or failed run has no
            # (or incomplete) row data, and would silently return empty/wrong results
            # instead of falling back to the last successfully completed run.
            latest = WorkspaceRun.query.filter_by(status='done').order_by(WorkspaceRun.triggered_at.desc()).first()
            run_id = latest.id if latest else None

        if run_id is None:
            return jsonify({'status': 'not_found', 'message': 'No workspace runs found'}), 404

        rows = (
            WorkspaceCastRow.query
            .filter_by(run_id=run_id)
            .limit(limit)
            .all()
        )
        return jsonify({'status': 'success', 'run_id': run_id, 'count': len(rows),
                        'rows': [r.to_dict() for r in rows]}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# Function: get_workspace_corent
@correlation_bp.route('/workspace/corent', methods=['GET'])
@cross_origin()
def get_workspace_corent():
    """Return enriched CORENT rows for the latest (or specified) workspace run."""
    try:
        from app.models.correlation_workspace import WorkspaceCorentRow, WorkspaceRun
        run_id = request.args.get('run_id', type=int)
        limit  = request.args.get('limit', 500, type=int)

        if run_id is None:
            # status='done' filter is required — an in-progress or failed run has no
            # (or incomplete) row data, and would silently return empty/wrong results
            # instead of falling back to the last successfully completed run.
            latest = WorkspaceRun.query.filter_by(status='done').order_by(WorkspaceRun.triggered_at.desc()).first()
            run_id = latest.id if latest else None

        if run_id is None:
            return jsonify({'status': 'not_found', 'message': 'No workspace runs found'}), 404

        rows = (
            WorkspaceCorentRow.query
            .filter_by(run_id=run_id)
            .limit(limit)
            .all()
        )
        return jsonify({'status': 'success', 'run_id': run_id, 'count': len(rows),
                        'rows': [r.to_dict() for r in rows]}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# Function: get_workspace_business
@correlation_bp.route('/workspace/business', methods=['GET'])
@cross_origin()
def get_workspace_business():
    """Return enriched Business Template rows for the latest (or specified) workspace run."""
    try:
        from app.models.correlation_workspace import WorkspaceBizRow, WorkspaceRun
        run_id = request.args.get('run_id', type=int)
        limit  = request.args.get('limit', 500, type=int)

        if run_id is None:
            # status='done' filter is required — an in-progress or failed run has no
            # (or incomplete) row data, and would silently return empty/wrong results
            # instead of falling back to the last successfully completed run.
            latest = WorkspaceRun.query.filter_by(status='done').order_by(WorkspaceRun.triggered_at.desc()).first()
            run_id = latest.id if latest else None

        if run_id is None:
            return jsonify({'status': 'not_found', 'message': 'No workspace runs found'}), 404

        rows = (
            WorkspaceBizRow.query
            .filter_by(run_id=run_id)
            .limit(limit)
            .all()
        )
        return jsonify({'status': 'success', 'run_id': run_id, 'count': len(rows),
                        'rows': [r.to_dict() for r in rows]}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# Function: get_workspace_correlations
@correlation_bp.route('/workspace/correlations', methods=['GET'])
@cross_origin()
def get_workspace_correlations():
    """
    Return workspace correlation records for the latest (or specified) run.

    Query parameters
    ----------------
    run_id       : int   (default: latest run)
    match_type   : 'three_way' | 'cast_biz' | 'cast_corent' | 'unmatched'  (optional filter)
    limit        : int   (default 500)
    """
    try:
        from app.models.correlation_workspace import WorkspaceCorrelation, WorkspaceRun
        run_id     = request.args.get('run_id', type=int)
        match_type = request.args.get('match_type')
        limit      = request.args.get('limit', 500, type=int)

        if run_id is None:
            # status='done' filter is required — an in-progress or failed run has no
            # (or incomplete) row data, and would silently return empty/wrong results
            # instead of falling back to the last successfully completed run.
            latest = WorkspaceRun.query.filter_by(status='done').order_by(WorkspaceRun.triggered_at.desc()).first()
            run_id = latest.id if latest else None

        if run_id is None:
            return jsonify({'status': 'not_found', 'message': 'No workspace runs found'}), 404

        query = WorkspaceCorrelation.query.filter_by(run_id=run_id)
        if match_type:
            query = query.filter_by(match_type=match_type)

        rows = query.limit(limit).all()
        return jsonify({
            'status': 'success',
            'run_id': run_id,
            'count': len(rows),
            'correlations': [r.to_dict() for r in rows],
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# Function: get_workspace_column_updates
@correlation_bp.route('/workspace/column-updates', methods=['GET'])
@cross_origin()
def get_workspace_column_updates():
    """
    Return AI-predicted column update traceability records.

    Query parameters
    ----------------
    run_id  : int    (default: latest run)
    source  : 'CAST' | 'CORENT' | 'Business'   (optional filter)
    column  : str    (optional column name filter)
    limit   : int    (default 1000)
    """
    try:
        from app.models.correlation_workspace import WorkspaceColumnUpdate, WorkspaceRun
        run_id = request.args.get('run_id', type=int)
        source = request.args.get('source')
        column = request.args.get('column')
        limit  = request.args.get('limit', 1000, type=int)

        if run_id is None:
            # status='done' filter is required — an in-progress or failed run has no
            # (or incomplete) row data, and would silently return empty/wrong results
            # instead of falling back to the last successfully completed run.
            latest = WorkspaceRun.query.filter_by(status='done').order_by(WorkspaceRun.triggered_at.desc()).first()
            run_id = latest.id if latest else None

        if run_id is None:
            return jsonify({'status': 'not_found', 'message': 'No workspace runs found'}), 404

        query = WorkspaceColumnUpdate.query.filter_by(run_id=run_id)
        if source:
            query = query.filter_by(source=source)
        if column:
            query = query.filter_by(column_name=column)

        rows = query.limit(limit).all()
        return jsonify({
            'status': 'success',
            'run_id': run_id,
            'count': len(rows),
            'updates': [r.to_dict() for r in rows],
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
