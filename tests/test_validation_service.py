"""
BMAD Dash - Validation Service Tests
Tests for Story 5.3: AI Agent Output Validation & Workflow Gap Warnings
"""
import pytest
from unittest.mock import Mock, MagicMock
from backend.services.validation_service import ValidationService, ValidationResult
from backend.models.git_evidence import GitCommit, GitEvidence
from backend.models.test_evidence import TestEvidence
from datetime import datetime


class TestValidationService:
    """Tests for ValidationService"""

    def setup_method(self):
        """Setup test fixtures"""
        self.project_root = "/test/project"
        self.validation_service = ValidationService(self.project_root)

        # Mock the dependencies
        self.validation_service.bmad_parser = Mock()
        self.validation_service.git_correlator = Mock()
        self.validation_service.test_discoverer = Mock()

    def test_validation_service_initialization(self):
        """Test that ValidationService initializes correctly"""
        service = ValidationService(self.project_root)
        assert service.project_root == self.project_root
        assert hasattr(service, 'bmad_parser')
        assert hasattr(service, 'git_correlator')
        assert hasattr(service, 'test_discoverer')

    def test_validate_story_all_evidence_present(self):
        """Test validate_story when all evidence is present"""
        # Setup mocks
        mock_story = Mock()
        mock_story.story_id = "5.3"
        mock_story.tasks = [Mock(status='done'), Mock(status='done')]
        mock_story.workflow_history = [
            {'name': 'dev-story', 'result': 'success'},
            {'name': 'code-review', 'result': 'success'}
        ]
        mock_story.gaps = []

        self.validation_service.bmad_parser.parse_project = Mock(return_value=Mock(
            epics=[Mock(stories=[mock_story])]
        ))

        # Mock Git evidence
        git_commits = [GitCommit(
            sha="abc123",
            message="Story 5.3: Implementation",
            author="test",
            timestamp=datetime.now(),
            files_changed=["file1.py"]
        )]
        self.validation_service.git_correlator.get_commits_for_story = Mock(return_value=git_commits)

        # Mock Test evidence
        test_evidence = TestEvidence(
            story_id="5.3",
            test_files=["test_story_5_3.py"],
            pass_count=18,
            fail_count=0,
            last_run_time=datetime.now(),
            status="green"
        )
        self.validation_service.test_discoverer.get_test_evidence_for_story = Mock(return_value=test_evidence)

        # Execute validation
        result = self.validation_service.validate_story("5.3")

        # Verify result
        assert isinstance(result, ValidationResult)
        assert result.story_id == "5.3"
        assert result.has_git_commits is True
        assert result.git_commit_count == 1
        assert result.has_tests is True
        assert result.test_pass_count == 18
        assert result.test_fail_count == 0
        assert result.all_tasks_complete is True
        assert result.has_dev_story_workflow is True
        assert result.has_code_review_workflow is True
        assert len(result.issues) == 0
        assert result.is_complete is True

    def test_validate_story_missing_git_commits(self):
        """Test validate_story when Git commits are missing"""
        # Setup mocks
        mock_story = Mock()
        mock_story.story_id = "5.3"
        mock_story.tasks = [Mock(status='done')]
        mock_story.workflow_history = []
        mock_story.gaps = []

        self.validation_service.bmad_parser.parse_project = Mock(return_value=Mock(
            epics=[Mock(stories=[mock_story])]
        ))

        # No Git commits
        self.validation_service.git_correlator.get_commits_for_story = Mock(return_value=[])

        # Mock Test evidence
        test_evidence = TestEvidence(story_id="5.3", test_files=[], status="unknown")
        self.validation_service.test_discoverer.get_test_evidence_for_story = Mock(return_value=test_evidence)

        # Execute validation
        result = self.validation_service.validate_story("5.3")

        # Verify result
        assert result.has_git_commits is False
        assert result.git_commit_count == 0
        assert any("Git commits" in issue for issue in result.issues)
        assert result.is_complete is False

    def test_validate_story_failing_tests(self):
        """Test validate_story when tests are failing"""
        # Setup mocks
        mock_story = Mock()
        mock_story.story_id = "5.3"
        mock_story.tasks = [Mock(status='done')]
        mock_story.workflow_history = []
        mock_story.gaps = []

        self.validation_service.bmad_parser.parse_project = Mock(return_value=Mock(
            epics=[Mock(stories=[mock_story])]
        ))

        # Mock Git evidence
        self.validation_service.git_correlator.get_commits_for_story = Mock(return_value=[
            GitCommit("abc", "test", "author", datetime.now())
        ])

        # Failing tests
        test_evidence = TestEvidence(
            story_id="5.3",
            test_files=["test_story_5_3.py"],
            pass_count=10,
            fail_count=5,
            failing_test_names=["test_validation", "test_gap_detection"],
            status="red"
        )
        self.validation_service.test_discoverer.get_test_evidence_for_story = Mock(return_value=test_evidence)

        # Execute validation
        result = self.validation_service.validate_story("5.3")

        # Verify result
        assert result.test_fail_count == 5
        assert any("failing tests" in issue.lower() for issue in result.issues)
        assert result.is_complete is False

    def test_validate_story_incomplete_tasks(self):
        """Test validate_story when tasks are incomplete"""
        # Setup mocks
        mock_story = Mock()
        mock_story.story_id = "5.3"
        mock_story.tasks = [
            Mock(status='done'),
            Mock(status='in-progress'),  # Incomplete task
            Mock(status='todo')  # Incomplete task
        ]
        mock_story.workflow_history = []
        mock_story.gaps = []

        self.validation_service.bmad_parser.parse_project = Mock(return_value=Mock(
            epics=[Mock(stories=[mock_story])]
        ))

        self.validation_service.git_correlator.get_commits_for_story = Mock(return_value=[])
        test_evidence = TestEvidence(story_id="5.3", status="unknown")
        self.validation_service.test_discoverer.get_test_evidence_for_story = Mock(return_value=test_evidence)

        # Execute validation
        result = self.validation_service.validate_story("5.3")

        # Verify result
        assert result.all_tasks_complete is False
        assert any("incomplete tasks" in issue.lower() for issue in result.issues)

    def test_validate_story_missing_code_review(self):
        """Test validate_story when code-review workflow is missing"""
        # Setup mocks
        mock_story = Mock()
        mock_story.story_id = "5.3"
        mock_story.tasks = [Mock(status='done')]
        mock_story.workflow_history = [
            {'name': 'dev-story', 'result': 'success'}
        ]
        mock_story.gaps = []

        self.validation_service.bmad_parser.parse_project = Mock(return_value=Mock(
            epics=[Mock(stories=[mock_story])]
        ))

        self.validation_service.git_correlator.get_commits_for_story = Mock(return_value=[
            GitCommit("abc", "test", "author", datetime.now())
        ])
        test_evidence = TestEvidence(story_id="5.3", pass_count=10, status="green")
        self.validation_service.test_discoverer.get_test_evidence_for_story = Mock(return_value=test_evidence)

        # Execute validation
        result = self.validation_service.validate_story("5.3")

        # Verify result
        assert result.has_code_review_workflow is False
        assert any("code-review" in issue.lower() for issue in result.issues)

    def test_detect_workflow_gaps_bulk_analysis(self):
        """Test detect_workflow_gaps for bulk project analysis"""
        # Setup mocks with multiple stories
        story1 = Mock()
        story1.story_id = "5.1"
        story1.gaps = []

        story2 = Mock()
        story2.story_id = "5.2"
        story2.gaps = [{'type': 'missing-code-review', 'message': 'Missing code-review'}]

        story3 = Mock()
        story3.story_id = "5.3"
        story3.gaps = [
            {'type': 'missing-dev-story', 'message': 'Missing dev-story'},
            {'type': 'test-gap', 'message': 'No passing tests'}
        ]

        self.validation_service.bmad_parser.parse_project = Mock(return_value=Mock(
            epics=[Mock(stories=[story1, story2, story3])]
        ))

        # Execute gap detection
        gaps = self.validation_service.detect_workflow_gaps()

        # Verify results
        assert len(gaps) == 2  # story2 and story3 have gaps
        assert any(gap['story_id'] == '5.2' for gap in gaps)
        assert any(gap['story_id'] == '5.3' for gap in gaps)

        # Story 5.3 should have 2 gap issues
        story_5_3_gaps = [gap for gap in gaps if gap['story_id'] == '5.3']
        assert len(story_5_3_gaps) > 0
        assert story_5_3_gaps[0]['gap_count'] == 2

    def test_validation_result_to_dict(self):
        """Test ValidationResult.to_dict() serialization"""
        result = ValidationResult(
            story_id="5.3",
            has_git_commits=True,
            git_commit_count=5,
            git_last_commit_time=datetime(2026, 1, 11, 10, 0, 0),
            has_tests=True,
            test_pass_count=18,
            test_fail_count=0,
            test_last_run_time=datetime(2026, 1, 11, 9, 0, 0),
            all_tasks_complete=True,
            has_dev_story_workflow=True,
            has_code_review_workflow=True,
            workflow_gaps=[],
            issues=[],
            is_complete=True
        )

        result_dict = result.to_dict()

        # Verify dict structure
        assert result_dict['story_id'] == "5.3"
        assert result_dict['has_git_commits'] is True
        assert result_dict['git_commit_count'] == 5
        assert 'git_last_commit_time' in result_dict
        assert result_dict['test_pass_count'] == 18
        assert result_dict['is_complete'] is True

    def test_validation_performance_under_500ms(self):
        """Test that validation completes in <500ms (AC5)"""
        import time

        # Setup minimal mocks
        mock_story = Mock()
        mock_story.story_id = "5.3"
        mock_story.tasks = []
        mock_story.workflow_history = []
        mock_story.gaps = []

        self.validation_service.bmad_parser.parse_project = Mock(return_value=Mock(
            epics=[Mock(stories=[mock_story])]
        ))
        self.validation_service.git_correlator.get_commits_for_story = Mock(return_value=[])
        self.validation_service.test_discoverer.get_test_evidence_for_story = Mock(
            return_value=TestEvidence(story_id="5.3", status="unknown")
        )

        # Measure validation time
        start_time = time.perf_counter()
        result = self.validation_service.validate_story("5.3")
        end_time = time.perf_counter()

        elapsed_ms = (end_time - start_time) * 1000

        # Verify performance requirement
        assert elapsed_ms < 500, f"Validation took {elapsed_ms:.2f}ms, exceeds 500ms NFR requirement"

    def test_story_not_found(self):
        """Test validation when story doesn't exist"""
        # Empty project
        self.validation_service.bmad_parser.parse_project = Mock(return_value=Mock(epics=[]))

        result = self.validation_service.validate_story("999.999")

        # Should return a result indicating story not found
        assert result.story_id == "999.999"
        assert any("not found" in issue.lower() for issue in result.issues)
        assert result.is_complete is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
