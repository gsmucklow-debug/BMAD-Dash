"""
BMAD Dash - Review Evidence API Endpoint
GET /api/review-evidence/<story_id> - Checks for code review artifacts
"""
import os
import glob
import logging
from flask import Blueprint, jsonify, request

logger = logging.getLogger(__name__)

review_evidence_bp = Blueprint('review_evidence', __name__)

@review_evidence_bp.route('/api/review-evidence/<story_id>', methods=['GET'])
def get_review_evidence(story_id):
    try:
        project_root = request.args.get('project_root')
        if not project_root:
            return jsonify({'error': 'MissingParameter', 'message': 'project_root required'}), 400
            
        # Normalize story ID (e.g. "1.3" -> "1-3")
        normalized = story_id.replace('.', '-')
        
        # Look for code-review-*.md in artifacts
        pattern = os.path.join(project_root, "_bmad-output", "implementation-artifacts", f"code-review-{normalized}.md")
        matches = glob.glob(pattern)
        
        if matches:
            return jsonify({
                'status': 'reviewed',
                'file': os.path.basename(matches[0]),
                'path': matches[0]
            })
        
        return jsonify({'status': 'pending'})
        
    except Exception as e:
        logger.error(f"Error checking review evidence: {e}")
        return jsonify({'error': 'InternalError', 'message': str(e)}), 500
