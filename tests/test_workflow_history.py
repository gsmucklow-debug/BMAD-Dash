"""
BMAD Dash - Workflow History & Gap Detection Tests
Tests for workflow history parsing and gap detection logic
"""
import pytest
from backend.parsers.bmad_parser import BMADParser
from backend.models.story import Story
import tempfile
import os


class TestWorkflowHistoryAndGapDetection:
    """Tests for workflow history parsing and gap detection"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.implementation_artifacts = os.path.join(self.temp_dir, "_bmad-output", "implementation-artifacts")
        os.makedirs(self.implementation_artifacts, exist_ok=True)
        
        # Create a test story file with workflow history
        self.story_file = os.path.join(self.implementation_artifacts, "4-2-workflow-history-gap-detection.md")
        self._create_test_story_file()
        
        # Create sprint-status.yaml
        self.sprint_status_file = os.path.join(self.implementation_artifacts, "sprint-status.yaml")
        self._create_sprint_status_file()
        
        # Initialize parser
        self.parser = BMADParser(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def _create_test_story_file(self):
        """Create a test story file with workflow history"""
        content = """---
story_id: "4.2"
title: "Workflow History & Gap Detection"
epic: "epic-4"
status: "in-progress"
last_updated: "2026-01-10"
workflow_history:
  - name: "dev-story"
    timestamp: "2026-01-10T10:00:00Z"
    result: "success"
  - name: "code-review"
    timestamp: "2026-01-10T11:00:00Z"
    result: "success"
---

# Story 4.2: Workflow History & Gap Detection

## Acceptance Criteria

### Workflow History Display
- [ ] **Chronological History**
    - [ ] Displays execution sequence with timestamps.
    - [ ] Entries are ordered chronologically (most recent first).
    - [ ] Each entry shows: workflow name, timestamp, and result status.
- [ ] **Visibility**
    - [ ] Workflow history is easily accessible on the dashboard for each story.

### Gap Detection Logic
- [ ] **Gap Identification**
    - [ ] Detects if story is "done" but no `dev-story` workflow was ever run.
    - [ ] Detects if `dev-story` is complete but no `code-review` was executed.
    - [ ] Detects if `code-review` is done but 0 passing tests are found (test-gap).
- [ ] **Warning & Suggestions**
    - [ ] Displays prominent warning: e.g., "⚠️ Missing: code-review workflow".
    - [ ] Suggests the next correct command to execute to close the gap.
    - [ ] Gap detection triggers automatically on dashboard load.
"""
        with open(self.story_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _create_sprint_status_file(self):
        """Create a test sprint-status.yaml"""
        content = """# generated: 2026-01-10
# project: BMAD Dash
# project_key: bmad-dash
# tracking_system: file-system
# story_location: _bmad-output/implementation-artifacts

development_status:
  epic-4: in-progress
  4-2-workflow-history-gap-detection: in-progress
"""
        with open(self.sprint_status_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def test_extract_workflow_history(self):
        """Test that workflow history is extracted from story frontmatter"""
        # Parse the story file
        story = self.parser._parse_story_file({
            'story_key': '4-2-workflow-history-gap-detection',
            'story_id': '4.2',
            'title': 'Workflow History & Gap Detection',
            'status': 'in-progress',
            'epic': 4
        })
        
        # Verify workflow_history is populated
        assert story is not None, "Story should be parsed"
        assert hasattr(story, 'workflow_history'), "Story should have workflow_history attribute"
        
        # Verify workflow history content (sorted by timestamp, most recent first)
        workflows = story.workflow_history
        assert len(workflows) == 2, f"Expected 2 workflows, got {len(workflows)}"

        # Verify workflow order and content (sorted by timestamp, most recent first)
        # code-review has timestamp 11:00, dev-story has 10:00, so code-review should be first
        assert workflows[0]['name'] == 'code-review', "First workflow should be code-review (most recent)"
        assert workflows[0]['result'] == 'success'
        assert workflows[1]['name'] == 'dev-story', "Second workflow should be dev-story (older)"
        assert workflows[1]['result'] == 'success'
        
        # Verify timestamps
        assert 'timestamp' in workflows[0], "Workflow should have timestamp"
        assert 'timestamp' in workflows[1], "Workflow should have timestamp"
    
    def test_extract_workflow_history_empty(self):
        """Test that empty workflow history is handled correctly"""
        # Create a story without workflows
        story_file_no_workflows = os.path.join(self.implementation_artifacts, "4-2-no-workflows.md")
        content = """---
story_id: "4.2"
title: "Story Without Workflows"
epic: "epic-4"
status: "in-progress"
---

# Story content
"""
        with open(story_file_no_workflows, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Parse the story file
        story = self.parser._parse_story_file({
            'story_key': '4-2-no-workflows',
            'story_id': '4.2',
            'title': 'Story Without Workflows',
            'status': 'in-progress',
            'epic': 4
        })
        
        # Verify workflow_history is empty list
        assert story is not None, "Story should be parsed"
        assert story.workflow_history == [], f"Expected empty workflows, got {story.workflow_history}"
    
    def test_detect_gap_missing_dev_story(self):
        """Test gap detection for missing dev-story workflow"""
        # Create a story marked as done without dev-story workflow
        story_file_done_no_dev = os.path.join(self.implementation_artifacts, "4-2-done-no-dev.md")
        content = """---
story_id: "4.2"
title: "Story Done Without Dev Story"
epic: "epic-4"
status: "done"
workflow_history:
  - name: "code-review"
    timestamp: "2026-01-10T11:00:00Z"
    result: "success"
---

# Story content
"""
        with open(story_file_done_no_dev, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Parse the story file
        story = self.parser._parse_story_file({
            'story_key': '4-2-done-no-dev',
            'story_id': '4.2',
            'title': 'Story Done Without Dev Story',
            'status': 'done',
            'epic': 4
        })
        
        # Verify gap is detected
        assert story is not None, "Story should be parsed"
        assert len(story.gaps) > 0, "Should detect at least one gap"
        
        # Verify gap details
        gap = story.gaps[0]
        assert gap['type'] == 'missing-dev-story', "Gap type should be missing-dev-story"
        assert '⚠️' in gap['message'], "Gap message should contain warning emoji"
        assert 'dev-story' in gap['message'], "Gap message should mention dev-story"
        assert gap['suggested_command'] == '/bmad:bmm:workflows:dev-story', "Gap should suggest dev-story command"
        assert gap['severity'] == 'high', "Gap severity should be high"
    
    def test_detect_gap_missing_code_review(self):
        """Test gap detection for missing code-review workflow"""
        # Create a story with dev-story but no code-review
        story_file_no_review = os.path.join(self.implementation_artifacts, "4-2-dev-no-review.md")
        content = """---
story_id: "4.2"
title: "Story Dev Without Code Review"
epic: "epic-4"
status: "in-progress"
workflow_history:
  - name: "dev-story"
    timestamp: "2026-01-10T10:00:00Z"
    result: "success"
---

# Story content
"""
        with open(story_file_no_review, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Parse the story file
        story = self.parser._parse_story_file({
            'story_key': '4-2-dev-no-review',
            'story_id': '4.2',
            'title': 'Story Dev Without Code Review',
            'status': 'in-progress',
            'epic': 4
        })
        
        # Verify gap is detected
        assert story is not None, "Story should be parsed"
        assert len(story.gaps) > 0, "Should detect at least one gap"
        
        # Verify gap details
        gap = story.gaps[0]
        assert gap['type'] == 'missing-code-review', "Gap type should be missing-code-review"
        assert 'code-review' in gap['message'], "Gap message should mention code-review"
        assert gap['suggested_command'] == '/bmad:bmm:workflows:code-review', "Gap should suggest code-review command"
        assert gap['severity'] == 'medium', "Gap severity should be medium"
    
    def test_no_gaps_when_complete(self):
        """Test that no gaps are detected when workflows are complete"""
        # Create a story with all workflows
        story_file_complete = os.path.join(self.implementation_artifacts, "4-2-complete.md")
        content = """---
story_id: "4.2"
title: "Complete Story"
epic: "epic-4"
status: "in-progress"
workflow_history:
  - name: "dev-story"
    timestamp: "2026-01-10T10:00:00Z"
    result: "success"
  - name: "code-review"
    timestamp: "2026-01-10T11:00:00Z"
    result: "success"
---

# Story content
"""
        with open(story_file_complete, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Parse the story file
        story = self.parser._parse_story_file({
            'story_key': '4-2-complete',
            'story_id': '4.2',
            'title': 'Complete Story',
            'status': 'in-progress',
            'epic': 4
        })
        
        # Verify no gaps are detected
        assert story is not None, "Story should be parsed"
        assert len(story.gaps) == 0, f"Should have no gaps, got {len(story.gaps)}"
    
    def test_gap_detection_performance(self):
        """Test that gap detection completes within 50ms (NFR requirement)"""
        import time
        
        # Create multiple stories for testing
        for i in range(10):
            story_file = os.path.join(self.implementation_artifacts, f"4-2-perf-{i}.md")
            content = f"""---
story_id: "4.2"
title: "Performance Test Story {i}"
epic: "epic-4"
status: "in-progress"
---

# Story content
"""
            with open(story_file, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # Measure gap detection time
        start_time = time.perf_counter()
        
        for i in range(10):
            story = self.parser._parse_story_file({
                'story_key': f'4-2-perf-{i}',
                'story_id': '4.2',
                'title': f'Performance Test Story {i}',
                'status': 'in-progress',
                'epic': 4
            })
            _ = story.gaps  # Access gaps to trigger detection
        
        end_time = time.perf_counter()
        elapsed_ms = (end_time - start_time) * 1000
        
        # Verify performance requirement (<50ms)
        assert elapsed_ms < 50, f"Gap detection took {elapsed_ms:.2f}ms, exceeds 50ms NFR requirement"
    
    def test_workflow_history_to_dict(self):
        """Test that Story.to_dict includes workflow_history and gaps"""
        # Parse the story file
        story = self.parser._parse_story_file({
            'story_key': '4-2-workflow-history-gap-detection',
            'story_id': '4.2',
            'title': 'Workflow History & Gap Detection',
            'status': 'in-progress',
            'epic': 4
        })
        
        # Convert to dict
        story_dict = story.to_dict()
        
        # Verify workflow_history and gaps are in dict
        assert 'workflow_history' in story_dict, "Story dict should include workflow_history"
        assert 'gaps' in story_dict, "Story dict should include gaps"
        assert len(story_dict['workflow_history']) == 2, "workflow_history should have 2 entries"
        assert isinstance(story_dict['gaps'], list), "gaps should be a list"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
