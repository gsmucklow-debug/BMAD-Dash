"""
BMAD Dash - Validation API Endpoints
Story 5.3: AI Agent Output Validation & Workflow Gap Warnings

GET /api/workflow-gaps - Returns workflow gaps for all stories in project
GET /api/validate-story/<story_id> - Returns validation result for a specific story
"""
import logging
from flask import Blueprint, jsonify, request
from backend.services.validation_service import ValidationService

logger = logging.getLogger(__name__)

validation_bp = Blueprint('validation', __name__)


@validation_bp.route('/api/workflow-gaps', methods=['GET'])
def get_workflow_gaps():
    """
    Returns workflow gaps for all stories in the project (AC3)

    Query Parameters:
        project_root: Path to the project (optional, defaults to current directory)

    Returns:
        JSON response with gaps array
    """
    try:
        # Extract project_root from query parameters
        project_root = request.args.get('project_root', '.')

        # Initialize ValidationService
        validation_service = ValidationService(project_root)

        # Detect workflow gaps
        gaps = validation_service.detect_workflow_gaps()

        logger.info(f"Workflow gaps detected: {len(gaps)} stories with gaps")

        return jsonify({
            'gaps': gaps,
            'count': len(gaps)
        }), 200

    except Exception as e:
        logger.error(f"Error detecting workflow gaps: {e}")
        return jsonify({
            'error': 'ValidationError',
            'message': 'Failed to detect workflow gaps',
            'details': str(e),
            'status': 500
        }), 500


@validation_bp.route('/api/validate-story/<story_id>', methods=['GET'])
def validate_story(story_id):
    """
    Returns comprehensive validation result for a specific story (AC1, AC2)

    Query Parameters:
        project_root: Path to the project (optional, defaults to current directory)

    Returns:
        JSON response with validation result
    """
    try:
        # Extract project_root from query parameters
        project_root = request.args.get('project_root', '.')

        # Initialize ValidationService
        validation_service = ValidationService(project_root)

        # Validate story
        validation_result = validation_service.validate_story(story_id)

        logger.info(f"Story {story_id} validated: is_complete={validation_result.is_complete}")

        return jsonify(validation_result.to_dict()), 200

    except Exception as e:
        logger.error(f"Error validating story {story_id}: {e}")
        return jsonify({
            'error': 'ValidationError',
            'message': f'Failed to validate story {story_id}',
            'details': str(e),
            'status': 500
        }), 500
