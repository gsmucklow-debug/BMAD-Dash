"""
API endpoints for BMAD documentation synchronization.
"""
from flask import Blueprint, request, jsonify
import logging
# from backend.api.bmad_sync import bmad_sync_bp  <-- REMOVED
from backend.services.bmad_sync import BMADSyncService
from backend.utils.error_handler import handle_api_errors

logger = logging.getLogger(__name__)

bmad_sync_bp = Blueprint('bmad_sync', __name__)


@bmad_sync_bp.route('/api/bmad-sync/status', methods=['GET'])
@handle_api_errors
def get_bmad_sync_status():
    """
    Get current BMAD documentation sync status.
    """
    project_root = request.args.get('project_root')
    if not project_root:
        raise ValueError("project_root parameter required")

    sync_service = BMADSyncService(project_root)
    status = sync_service.get_status()

    # Check for updates if it's time
    if sync_service.should_check_for_updates():
        update_info = sync_service.check_for_updates()
        if update_info:
            status['update_available'] = update_info.get('has_updates', False)
            status['latest_version'] = update_info.get('latest_version')
            status['last_check'] = update_info.get('last_check')
    else:
        status['update_available'] = False

    # Initialize with 'latest' if this is first run
    if status.get('current_version') == 'unknown':
        sync_service.mark_docs_seen('latest')
        status['current_version'] = 'latest'

    return jsonify(status)


@bmad_sync_bp.route('/api/bmad-sync/check', methods=['POST'])
@handle_api_errors
def check_bmad_updates():
    """
    Force check for BMAD documentation updates.
    """
    data = request.get_json()
    project_root = data.get('project_root')
    if not project_root:
        raise ValueError("project_root required")

    sync_service = BMADSyncService(project_root)
    update_info = sync_service.check_for_updates()

    return jsonify(update_info)


@bmad_sync_bp.route('/api/bmad-sync/perform', methods=['POST'])
@handle_api_errors
def perform_bmad_sync():
    """
    Perform the actual BMAD documentation sync (download and extract).
    """
    data = request.get_json()
    project_root = data.get('project_root')
    if not project_root:
        raise ValueError("project_root required")

    sync_service = BMADSyncService(project_root)
    result = sync_service.sync_docs()
    
    return jsonify(result), 200 if result.get('success') else 500


@bmad_sync_bp.route('/api/bmad-sync/update', methods=['POST'])
@handle_api_errors
def mark_docs_seen():
    """
    Mark documentation as seen (LEGACY: user has viewed the latest docs).
    Used for dismissing notifications without downloading.
    """
    data = request.get_json()
    project_root = data.get('project_root')
    version = data.get('version')
    if not project_root:
        raise ValueError("project_root required")

    sync_service = BMADSyncService(project_root)

    # If no version provided, try to get latest from site
    if not version:
        docs_info = sync_service.get_latest_docs_info()
        version = docs_info.get('version', 'latest') if docs_info else 'latest'

    result = sync_service.mark_docs_seen(version)
    return jsonify({
        **result,
        'docs_url': sync_service.docs_url
    }), 200
