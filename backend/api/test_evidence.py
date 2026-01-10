"""
BMAD Dash - Test Evidence API Endpoint
GET /api/test-evidence/<story_id> - Returns test results for a story
"""
import logging
import time
import os
import glob
import re
from flask import Blueprint, jsonify, request
from backend.services.test_discoverer import TestDiscoverer
from backend.utils.story_test_parser import parse_test_counts_from_story_file
from backend.models.test_evidence import TestEvidence

logger = logging.getLogger(__name__)

test_evidence_bp = Blueprint('test_evidence', __name__)


def _extract_story_id(story_id: str) -> str:
    """
    Extract epic.story format from various input formats

    Args:
        story_id: Input in various formats (e.g., "1.3", "story-1.3", "2-2")

    Returns:
        Normalized format like "1.3" or None if invalid
    """
    # Already in epic.story format
    if re.match(r'^\d+\.\d+$', story_id):
        return story_id

    # Extract from "story-1.3" or "Story 1.3" or "2-2" format
    match = re.search(r'(\d+)[.\-_\s](\d+)', story_id)
    if match:
        return f"{match.group(1)}.{match.group(2)}"

    return None


def _check_story_exists(story_id: str, project_root: str) -> bool:
    """
    Check if story file exists for the given story_id

    Args:
        story_id: Story identifier
        project_root: Project root path

    Returns:
        True if story file exists, False otherwise
    """
    # Normalize story_id to epic-story format (e.g., "1.3" -> "1-3")
    normalized = _extract_story_id(story_id)
    if not normalized:
        return False

    # Convert "1.3" to "1-3" for filename
    story_key = normalized.replace('.', '-')

    # Common story file locations
    possible_paths = [
        os.path.join(project_root, "_bmad-output", "implementation-artifacts", f"{story_key}-*.md"),
        os.path.join(project_root, "_bmad-output", "implementation", f"{story_key}-*.md"),
        os.path.join(project_root, "stories", f"{story_key}-*.md"),
    ]

    # Try to find story file
    for pattern in possible_paths:
        matches = glob.glob(pattern)
        if matches:
            return True

    return False


@test_evidence_bp.route('/api/test-evidence/<story_id>', methods=['GET'])
def get_test_evidence(story_id):
    """
    Returns test evidence for a specific story

    Query Parameters:
        project_root: Path to the project repository (required)

    Returns:
        JSON response with test evidence (total_tests, pass_count, fail_count,
        failing_test_names, status, last_run_time)
    """
    start_time = time.perf_counter()

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

        # Check if story exists (404 if not found)
        if not _check_story_exists(story_id, project_root):
            logger.warning(f"Story not found: {story_id}")
            return jsonify({
                'error': 'StoryNotFound',
                'message': f'Story {story_id} not found',
                'details': f'No story file found for story ID: {story_id}',
                'status': 404
            }), 404

        # Initialize TestDiscoverer
        discoverer = TestDiscoverer(project_root)

        # Get test evidence for story
        evidence = discoverer.get_test_evidence_for_story(story_id, project_root)

        # If no tests were found or all counts are 0, try parsing from story file
        if evidence.pass_count == 0 and evidence.fail_count == 0:
            logger.info(f"No test execution results for story {story_id}, attempting to parse from story file")
            parsed_counts = parse_test_counts_from_story_file(story_id, project_root)

            if parsed_counts:
                # Create new evidence with parsed counts
                evidence = TestEvidence(
                    story_id=story_id,
                    test_files=[],
                    pass_count=parsed_counts["pass_count"],
                    fail_count=parsed_counts["fail_count"],
                    failing_test_names=[],
                    last_run_time=None,
                    status=parsed_counts["status"]
                )
                logger.info(f"Using parsed test counts from story file: {parsed_counts['pass_count']}/{parsed_counts['total_tests']}")

        # Convert to dict for JSON response
        response = evidence.to_dict()

        # Calculate response time
        elapsed_time = (time.perf_counter() - start_time) * 1000  # Convert to ms

        # Log performance warning if slow (NFR5 requirement: <100ms)
        if elapsed_time > 100:
            logger.warning(f"Test evidence endpoint slow for story {story_id}: {elapsed_time:.2f}ms")

        logger.info(f"Test evidence retrieved for story {story_id}: {evidence.pass_count} passing, {evidence.fail_count} failing, status={evidence.status} ({elapsed_time:.2f}ms)")

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error getting test evidence for story {story_id}: {e}")
        return jsonify({
            'error': 'TestDiscoveryError',
            'message': 'Failed to retrieve test evidence',
            'details': str(e),
            'status': 500
        }), 500
