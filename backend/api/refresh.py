"""
BMAD Dash - Refresh API Endpoint
POST /api/refresh - Forces cache invalidation and re-parses artifacts
"""
from flask import Blueprint, jsonify

refresh_bp = Blueprint('refresh', __name__)


@refresh_bp.route('/api/refresh', methods=['POST'])
def refresh():
    """
    Forces cache refresh
    Will be implemented in Story 1.1
    """
    return jsonify({
        'status': 'not_implemented',
        'message': 'Refresh endpoint will be implemented in Story 1.1'
    }), 501
