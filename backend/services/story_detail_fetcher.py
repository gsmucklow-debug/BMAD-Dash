"""
Story Detail Fetcher Service
Extracts comprehensive story details (tasks, AC, status) for AI consumption
"""

import os
import re
from typing import Optional, Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class StoryDetailFetcher:
    """Fetches detailed story information from markdown files"""

    def __init__(self, project_root: str):
        """
        Initialize fetcher with project root

        Args:
            project_root: Path to project root directory
        """
        self.project_root = project_root
        self.implementation_artifacts = os.path.join(
            project_root, "_bmad-output", "implementation-artifacts"
        )

    def get_story_details(self, story_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch complete story details including tasks, AC, and metadata

        Args:
            story_id: Story ID in format "5.2"

        Returns:
            Dict with story details or None if not found
        """
        # Convert story_id "5.2" to filename pattern "5-2-*"
        epic_num, story_num = story_id.split('.')
        story_key = f"{epic_num}-{story_num}"

        # Find the story file
        story_file = self._find_story_file(story_key)
        if not story_file:
            logger.warning(f"Story file not found for {story_id}")
            return None

        try:
            with open(story_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse frontmatter
            frontmatter = self._parse_frontmatter(content)

            # Extract sections
            tasks = self._extract_tasks(content)
            acceptance_criteria = self._extract_acceptance_criteria(content)
            summary = self._extract_summary(content)

            return {
                'story_id': story_id,
                'title': frontmatter.get('title', 'Unknown'),
                'status': frontmatter.get('status', 'unknown'),
                'epic': frontmatter.get('epic', 'Unknown'),
                'created': frontmatter.get('created', 'Unknown'),
                'completed': frontmatter.get('completed'),
                'tasks': tasks,
                'acceptance_criteria': acceptance_criteria,
                'summary': summary,
                'total_tasks': len(tasks),
                'completed_tasks': sum(1 for t in tasks if t['status'] == 'done'),
                'raw_content': content
            }

        except Exception as e:
            logger.error(f"Error reading story file {story_file}: {e}")
            return None

    def _find_story_file(self, story_key: str) -> Optional[str]:
        """
        Find story file by pattern (e.g., "5-2-*")

        Args:
            story_key: Story key in format "epic-story" (e.g., "5-2")

        Returns:
            Full path to story file or None
        """
        if not os.path.exists(self.implementation_artifacts):
            return None

        # Look for files matching pattern
        import glob
        pattern = os.path.join(self.implementation_artifacts, f"{story_key}-*.md")
        matches = glob.glob(pattern)

        return matches[0] if matches else None

    def _parse_frontmatter(self, content: str) -> Dict[str, Any]:
        """
        Extract YAML frontmatter from markdown

        Args:
            content: Full markdown content

        Returns:
            Dict of frontmatter values
        """
        match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
        if not match:
            return {}

        frontmatter = {}
        for line in match.group(1).split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip().strip("'\"")
                frontmatter[key] = value

        return frontmatter

    def _extract_tasks(self, content: str) -> List[Dict[str, str]]:
        """
        Extract task list from markdown

        Args:
            content: Markdown content

        Returns:
            List of task dicts with title and status
        """
        tasks = []

        # Find Tasks section (flexible: "Tasks", "Implementation Tasks", etc.)
        tasks_match = re.search(r'## .*?Tasks\n(.*?)(?=\n## |\Z)', content, re.DOTALL | re.IGNORECASE)
        if not tasks_match:
            return tasks

        tasks_section = tasks_match.group(1)

        # Extract all task items (checkbox format)
        # Pattern: "- [x] Task name" or "* [ ] Task name"
        task_pattern = r'^\s*[-*]\s+\[([ xX])\]\s+(.+?)(?=\r?\n\s*[-*]|\Z)'

        for match in re.finditer(task_pattern, tasks_section, re.MULTILINE):
            checkbox = match.group(1)
            title = match.group(2).strip()

            # Clean up title (remove markdown links, bold, etc.)
            title = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', title)  # Remove markdown links
            title = re.sub(r'\*\*(.+?)\*\*', r'\1', title)      # Remove bold
            title = re.sub(r'__(.+?)__', r'\1', title)          # Remove alt bold

            status = 'done' if checkbox.lower() == 'x' else 'pending'
            tasks.append({
                'title': title,
                'status': status
            })

        return tasks

    def _extract_acceptance_criteria(self, content: str) -> List[str]:
        """
        Extract acceptance criteria from markdown

        Args:
            content: Markdown content

        Returns:
            List of AC descriptions
        """
        criteria = []

        # Find Acceptance Criteria section
        ac_match = re.search(r'## Acceptance Criteria\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
        if not ac_match:
            return criteria

        ac_section = ac_match.group(1)

        # Extract AC items (ACx: headers and content)
        ac_pattern = r'### (AC\d+:.*?)\n(.*?)(?=\n###|### AC|\Z)'

        for match in re.finditer(ac_pattern, ac_section, re.DOTALL):
            ac_title = match.group(1).strip()
            ac_content = match.group(2).strip()

            # Clean up content
            ac_content = re.sub(r'\*\*Given\*\*', 'Given', ac_content)
            ac_content = re.sub(r'\*\*When\*\*', 'When', ac_content)
            ac_content = re.sub(r'\*\*Then\*\*', 'Then', ac_content)
            ac_content = re.sub(r'\n+', ' ', ac_content)  # Collapse newlines

            criteria.append(f"{ac_title}: {ac_content}")

        return criteria

    def _extract_summary(self, content: str) -> str:
        """
        Extract user story summary from markdown

        Args:
            content: Markdown content

        Returns:
            User story text
        """
        # Find User Story section
        summary_match = re.search(r'## User Story\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
        if summary_match:
            return summary_match.group(1).strip()

        return ""
