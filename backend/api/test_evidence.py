"""
BMAD Dash - Test Evidence API Endpoint
GET /api/test-evidence/<story_id> - Returns test results for a story
"""
from flask import Blueprint, jsonify

test_evidence_bp = Blueprint('test_evidence', __name__)


@test_evidence_bp.route('/api/test-evidence/<story_id>', methods=['GET'])
def get_test_evidence(story_id):
    """
    Returns test evidence for a specific story
    Will be implemented in Story 2.3
    """
    return jsonify({
        'status': 'not_implemented',
        'message': f'Test evidence endpoint will be implemented in Story 2.3',
        'story_id': story_id
    }), 501
