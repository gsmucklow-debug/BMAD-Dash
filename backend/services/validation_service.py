"""
BMAD Dash - Story Validation Service
Validates AI agent story completion by aggregating Git, test, task, and workflow evidence
Story 5.3: AI Agent Output Validation & Workflow Gap Warnings
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime

from backend.parsers.bmad_parser import BMADParser
from backend.services.git_correlator import GitCorrelator
from backend.services.test_discoverer import TestDiscoverer


@dataclass
class ValidationResult:
    """
    Comprehensive validation result for a story
    Aggregates evidence from Git, tests, tasks, and workflows
    """
    story_id: str
    has_git_commits: bool = False
    git_commit_count: int = 0
    git_last_commit_time: Optional[datetime] = None
    has_tests: bool = False
    test_pass_count: int = 0
    test_fail_count: int = 0
    test_last_run_time: Optional[datetime] = None
    all_tasks_complete: bool = False
    has_dev_story_workflow: bool = False
    has_code_review_workflow: bool = False
    workflow_gaps: List[Dict[str, Any]] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)
    is_complete: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for JSON responses"""
        return {
            "story_id": self.story_id,
            "has_git_commits": self.has_git_commits,
            "git_commit_count": self.git_commit_count,
            "git_last_commit_time": self.git_last_commit_time.isoformat() if self.git_last_commit_time else None,
            "has_tests": self.has_tests,
            "test_pass_count": self.test_pass_count,
            "test_fail_count": self.test_fail_count,
            "test_last_run_time": self.test_last_run_time.isoformat() if self.test_last_run_time else None,
            "all_tasks_complete": self.all_tasks_complete,
            "has_dev_story_workflow": self.has_dev_story_workflow,
            "has_code_review_workflow": self.has_code_review_workflow,
            "workflow_gaps": self.workflow_gaps,
            "issues": self.issues,
            "is_complete": self.is_complete
        }


class ValidationService:
    """
    Validates story completion by aggregating evidence from multiple sources

    Evidence Sources:
    - Git commits (from GitCorrelator)
    - Test results (from TestDiscoverer)
    - Task completion (from BMADParser)
    - Workflow history (from BMADParser)
    """

    def __init__(self, project_root: str):
        """
        Initialize validation service with project root

        Args:
            project_root: Path to project root directory
        """
        self.project_root = project_root
        self.bmad_parser = BMADParser(project_root)
        self.git_correlator = GitCorrelator(project_root)
        self.test_discoverer = TestDiscoverer(project_root)

    def validate_story(self, story_id: str) -> ValidationResult:
        """
        Validate story completion by aggregating all evidence sources

        This method checks:
        - Git commits exist for the story (AC1)
        - Tests exist and are passing (AC1)
        - All tasks are marked complete (AC1)
        - Required workflows were executed (AC1)

        Args:
            story_id: Story identifier (e.g., "5.3")

        Returns:
            ValidationResult with comprehensive evidence summary
        """
        result = ValidationResult(story_id=story_id)

        # Find the story in the project
        story = self._find_story(story_id)

        if not story:
            result.issues.append(f"Story {story_id} not found in project")
            return result

        # 1. Validate Git Evidence
        git_commits = self.git_correlator.get_commits_for_story(story_id)
        result.has_git_commits = len(git_commits) > 0
        result.git_commit_count = len(git_commits)

        if git_commits:
            result.git_last_commit_time = self.git_correlator.get_last_commit_time(git_commits)

        if not result.has_git_commits:
            result.issues.append("No Git commits found for this story")

        # 2. Validate Test Evidence
        test_evidence = self.test_discoverer.get_test_evidence_for_story(story_id, self.project_root)
        result.has_tests = test_evidence.total_tests > 0
        result.test_pass_count = test_evidence.pass_count
        result.test_fail_count = test_evidence.fail_count
        result.test_last_run_time = test_evidence.last_run_time

        if not result.has_tests:
            result.issues.append("No tests found for this story")
        elif result.test_fail_count > 0:
            result.issues.append(f"{result.test_fail_count} failing tests detected")

        # 3. Validate Task Completion
        complete_tasks = sum(1 for task in story.tasks if task.status == 'done')
        total_tasks = len(story.tasks)
        result.all_tasks_complete = complete_tasks == total_tasks and total_tasks > 0

        if not result.all_tasks_complete:
            incomplete_count = total_tasks - complete_tasks
            if incomplete_count > 0:
                result.issues.append(f"{incomplete_count} incomplete tasks remaining")

        # 4. Validate Workflow History
        workflow_names = {wf.get('name', '') for wf in story.workflow_history if isinstance(wf, dict)}
        result.has_dev_story_workflow = 'dev-story' in workflow_names
        result.has_code_review_workflow = 'code-review' in workflow_names

        if not result.has_dev_story_workflow:
            result.issues.append("Missing dev-story workflow execution")

        if result.has_dev_story_workflow and not result.has_code_review_workflow:
            result.issues.append("Missing code-review workflow execution")

        # 5. Include workflow gaps from BMADParser
        result.workflow_gaps = story.gaps

        # 6. Determine overall completion status
        result.is_complete = (
            result.has_git_commits and
            result.has_tests and
            result.test_fail_count == 0 and
            result.all_tasks_complete and
            result.has_dev_story_workflow and
            result.has_code_review_workflow and
            len(result.workflow_gaps) == 0
        )

        return result

    def detect_workflow_gaps(self) -> List[Dict[str, Any]]:
        """
        Detect workflow gaps across all stories in the project (AC3)

        Identifies stories with workflow execution gaps:
        - Story marked "done" without dev-story workflow
        - dev-story complete but no code-review
        - code-review done but 0 passing tests

        Returns:
            List of gap summaries with story_id, gap details, and suggested actions
        """
        gaps = []

        # Parse project to get all stories
        project = self.bmad_parser.parse_project()

        if not project:
            return gaps

        # Iterate through all epics and stories
        for epic in project.epics:
            for story in epic.stories:
                # Check if story has any gaps
                if len(story.gaps) > 0:
                    gap_summary = {
                        'story_id': story.story_id,
                        'story_key': story.story_key,
                        'story_title': story.title,
                        'story_status': story.status,
                        'gap_count': len(story.gaps),
                        'gaps': story.gaps
                    }
                    gaps.append(gap_summary)

        return gaps

    def _find_story(self, story_id: str):
        """
        Find a story by ID in the project

        Args:
            story_id: Story identifier (e.g., "5.3")

        Returns:
            Story object or None if not found
        """
        project = self.bmad_parser.parse_project()

        if not project:
            return None

        for epic in project.epics:
            for story in epic.stories:
                if story.story_id == story_id:
                    return story

        return None
