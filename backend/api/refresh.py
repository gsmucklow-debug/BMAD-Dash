"""
BMAD Dash - Refresh API Endpoint
POST /api/refresh - Forces cache invalidation and re-parses artifacts
Story 3.3: Minimal List View & Manual Refresh
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
import logging

# Import the shared cache instance from dashboard
from backend.api.dashboard import _cache

refresh_bp = Blueprint('refresh', __name__)
logger = logging.getLogger(__name__)


@refresh_bp.route('/api/refresh', methods=['POST'])
def refresh():
    """
    Forces cache refresh by clearing project-state.json
    
    Query Parameters:
        project_root (str): Path to the BMAD project root
        
    Returns:
        JSON response with cache clear status and timestamp
    """
    start_time = datetime.now()
    
    # Get project_root from query parameters
    project_root = request.args.get('project_root')
    
    if not project_root:
        logger.warning('Refresh called without project_root parameter')
        return jsonify({
            'error': 'MissingParameter',
            'message': 'project_root query parameter is required'
        }), 400
        
    try:
        # Delete project-state.json to force full bootstrap on next request
        import os
        cache_file = os.path.join(project_root, "_bmad-output/implementation-artifacts/project-state.json")
        deleted = False
        if os.path.exists(cache_file):
            os.remove(cache_file)
            deleted = True
            
        # Also clear legacy cache if it exists (for safety)
        if _cache:
            _cache.invalidate_all()
            
        end_time = datetime.now()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        logger.info(f'Cache cleared (deleted={deleted}) for {project_root}')
        
        return jsonify({
            'status': 'cache_cleared',
            'deleted_file': deleted,
            'project_root': project_root,
            'timestamp': end_time.isoformat(),
            'duration_ms': round(duration_ms, 2),
            'message': 'Cache cleared. Next request will rebuild project state.'
        }), 200
        
    except Exception as e:
        logger.error(f'Cache clear failed: {str(e)}', exc_info=True)
        return jsonify({
            'error': 'RefreshError',
            'message': 'Failed to clear cache',
            'details': str(e)
        }), 500
