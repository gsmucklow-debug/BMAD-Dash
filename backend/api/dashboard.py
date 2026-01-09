"""
BMAD Dash - Dashboard API Endpoint
GET /api/dashboard - Returns project overview with epics and stories
"""
from flask import Blueprint, jsonify

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    """
    Returns dashboard data including project overview, epics, and stories
    Will be implemented in Story 1.1
    """
    return jsonify({
        'status': 'not_implemented',
        'message': 'Dashboard endpoint will be implemented in Story 1.1'
    }), 501
