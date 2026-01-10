"""
BMAD Dash - Git Evidence API Endpoint
GET /api/git-evidence/<story_id> - Returns Git commits for a story
"""
import logging
from flask import Blueprint, jsonify, request
from backend.services.git_correlator import GitCorrelator
from backend.models.git_evidence import GitEvidence

logger = logging.getLogger(__name__)

git_evidence_bp = Blueprint('git_evidence', __name__)


@git_evidence_bp.route('/api/git-evidence/<story_id>', methods=['GET'])
def get_git_evidence(story_id):
    """
    Returns Git evidence for a specific story
    
    Query Parameters:
        project_root: Path to the project repository
    
    Returns:
        JSON response with commits, status, and last_commit_time
    """
    try:
        # Extract project_root from query parameters
        project_root = request.args.get('project_root')
        
        if not project_root:
            return jsonify({
                'error': 'MissingParameter',
                'message': 'project_root query parameter is required',
                'details': 'Provide project_root=/path/to/project',
                'status': 400
            }), 400
        
        # Initialize GitCorrelator
        correlator = GitCorrelator(project_root)
        
        # Get commits for story with fallback to file mtime (NFR22)
        commits = correlator.get_commits_with_fallback(story_id, project_root)
        
        # Calculate status
        status, last_commit_time = correlator.calculate_status(commits)
        
        # Build GitEvidence response
        evidence = GitEvidence(
            story_id=story_id,
            commits=commits
        )
        
        # Convert to dict and add status info
        response = evidence.to_dict()
        response['status'] = status
        response['last_commit_time'] = last_commit_time.isoformat() if last_commit_time else None
        
        logger.info(f"Git evidence retrieved for story {story_id}: {len(commits)} commits, status={status}")
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error getting Git evidence for story {story_id}: {e}")
        return jsonify({
            'error': 'GitCorrelationError',
            'message': 'Failed to retrieve Git evidence',
            'details': str(e),
            'status': 500
        }), 500
