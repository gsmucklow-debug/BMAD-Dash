"""
BMAD Dash - Git Evidence API Endpoint
GET /api/git-evidence/<story_id> - Returns Git commits for a story
"""
from flask import Blueprint, jsonify

git_evidence_bp = Blueprint('git_evidence', __name__)


@git_evidence_bp.route('/api/git-evidence/<story_id>', methods=['GET'])
def get_git_evidence(story_id):
    """
    Returns Git evidence for a specific story
    Will be implemented in Story 2.2
    """
    return jsonify({
        'status': 'not_implemented',
        'message': f'Git evidence endpoint will be implemented in Story 2.2',
        'story_id': story_id
    }), 501
