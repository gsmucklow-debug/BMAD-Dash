"""
BMAD Dash - Story Test Count Parser
Parses test counts from story markdown files
"""
import os
import re
import glob
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)


def extract_story_id(story_id: str) -> Optional[str]:
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


def parse_test_counts_from_story_file(story_id: str, project_root: str) -> Optional[Dict]:
    """
    Parse test counts from story markdown file

    Args:
        story_id: Story identifier (e.g., "1.2")
        project_root: Project root path

    Returns:
        Dict with pass_count, fail_count, total_tests, status or None if not found
    """
    # Normalize story_id
    normalized = extract_story_id(story_id)
    if not normalized:
        logger.debug(f"Invalid story_id format: {story_id}")
        return None

    # Convert "1.3" to "1-3" for filename
    story_key = normalized.replace('.', '-')

    # Search for story file
    possible_paths = [
        os.path.join(project_root, "_bmad-output", "implementation-artifacts", f"{story_key}-*.md"),
        os.path.join(project_root, "_bmad-output", "implementation", f"{story_key}-*.md"),
        os.path.join(project_root, "stories", f"{story_key}-*.md"),
    ]

    story_file = None
    for pattern in possible_paths:
        matches = glob.glob(pattern)
        if matches:
            story_file = matches[0]
            break

    if not story_file:
        logger.debug(f"Story file not found for {story_id}")
        return None

    try:
        with open(story_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Look for test count patterns like:
        # "22/22 passing" or "Tests: 22/22" or "Test Results: 22/22 passing"
        patterns = [
            r'(\d+)/(\d+)\s+passing',            # "22/22 passing"
            r'passing\s*\((\d+)/(\d+)',          # "passing (22/22 tests)"
            r'Tests?:\s*(\d+)/(\d+)',            # "Tests: 22/22"
            r'Test Results?:\s*(\d+)/(\d+)',     # "Test Results: 22/22"
            r'All\s+(\d+)\s+tests?\s+passing',   # "All 101 tests passing"
            r'(\d+)\s+tests?,\s*all passing',    # "22 tests, all passing"
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:
                    passing = int(match.group(1))
                    total = int(match.group(2))
                    failing = total - passing
                else:
                    # Pattern like "22 tests, all passing"
                    passing = int(match.group(1))
                    total = passing
                    failing = 0

                logger.info(f"Parsed test counts from story file {story_id}: {passing}/{total}")
                return {
                    "pass_count": passing,
                    "fail_count": failing,
                    "total_tests": total,
                    "status": "green" if failing == 0 else "red"
                }

        logger.debug(f"No test count patterns found in story file {story_id}")
        return None

    except Exception as e:
        logger.warning(f"Error parsing test counts from story file {story_id}: {e}")
        return None
