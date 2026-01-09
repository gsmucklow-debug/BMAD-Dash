"""
BMAD Dash - Parser Tests
Tests for YAML, Markdown, and BMAD parsers
"""
import pytest
import os
import tempfile
from backend.parsers.yaml_parser import YAMLParser
from backend.parsers.markdown_parser import MarkdownParser
from backend.parsers.bmad_parser import BMADParser


class TestYAMLParser:
    """Test YAML frontmatter parser"""
    
    def test_parse_valid_frontmatter(self):
        """Test parsing valid YAML frontmatter"""
        content = """---
story_id: "1.1"
title: "Test Story"
status: "done"
---
# Story Content
This is the markdown content.
"""
        result = YAMLParser.parse_frontmatter(content, "test.md")
        
        assert result['frontmatter']['story_id'] == "1.1"
        assert result['frontmatter']['title'] == "Test Story"
        assert result['frontmatter']['status'] == "done"
        assert "# Story Content" in result['content']
        assert 'error' not in result
    
    def test_parse_malformed_yaml(self):
        """Test parsing malformed YAML returns error"""
        content = """---
story_id: "1.1
bad yaml: [ unclosed
---
# Content
"""
        result = YAMLParser.parse_frontmatter(content, "test.md")
        
        assert 'error' in result
        assert "Malformed YAML" in result['error']
        assert "test.md" in result['error']
    
    def test_parse_missing_closing_delimiter(self):
        """Test YAML with missing closing delimiter"""
        content = """---
story_id: "1.1"
title: "Test"
# Missing closing ---
"""
        result = YAMLParser.parse_frontmatter(content, "test.md")
        
        assert 'error' in result
        assert "Missing closing" in result['error']
    
    def test_parse_pure_yaml_file(self):
        """Test parsing pure YAML file (no frontmatter delimiters)"""
        content = """project_name: BMAD Dash
epics:
  - epic_id: 1
    title: Test Epic
"""
        result = YAMLParser.parse_yaml_file(content, "sprint-status.yaml")
        
        assert result['project_name'] == "BMAD Dash"
        assert len(result['epics']) == 1
        assert result['epics'][0]['title'] == "Test Epic"
    
    def test_parse_empty_content(self):
        """Test parsing empty content"""
        result = YAMLParser.parse_frontmatter("", "empty.md")
        
        assert result['frontmatter'] == {}
        assert result['content'] == ""


class TestMarkdownParser:
    """Test Markdown content parser"""
    
    def test_extract_tasks(self):
        """Test extracting tasks from markdown"""
        content = """
# Tasks
- [ ] Uncompleted task 1
- [x] Completed task 2
- [ ] Task with subtasks
  - [x] Subtask 1
  - [ ] Subtask 2
"""
        result = MarkdownParser.parse_content(content)
        tasks = result['tasks']
        
        assert len(tasks) == 3
        assert tasks[0]['title'] == "Uncompleted task 1"
        assert tasks[0]['status'] == "todo"
        assert tasks[1]['title'] == "Completed task 2"
        assert tasks[1]['status'] == "done"
        assert len(tasks[2]['subtasks']) == 2
        assert tasks[2]['subtasks'][0]['status'] == "done"
    
    def test_extract_acceptance_criteria(self):
        """Test extracting acceptance criteria"""
        content = """
## Acceptance Criteria

**Given** a BMAD project  
**When** the parser is executed  
**Then** data is populated  

**And** errors are handled gracefully
"""
        result = MarkdownParser.parse_content(content)
        criteria = result['acceptance_criteria']
        
        assert len(criteria) == 4
        assert "**Given**" in criteria[0]
        assert "**When**" in criteria[1]
        assert "**Then**" in criteria[2]
        assert "**And**" in criteria[3]
    
    def test_extract_headings(self):
        """Test extracting markdown headings"""
        content = """# Heading 1
## Heading 2
### Heading 3
"""
        result = MarkdownParser.parse_content(content)
        headings = result['headings']
        
        assert len(headings) == 3
        assert headings[0]['level'] == 1
        assert headings[0]['text'] == "Heading 1"
        assert headings[1]['level'] == 2
        assert headings[2]['level'] == 3
    
    def test_empty_content(self):
        """Test parsing empty markdown"""
        result = MarkdownParser.parse_content("")
        
        assert result['tasks'] == []
        assert result['acceptance_criteria'] == []
        assert result['headings'] == []


class TestBMADParser:
    """Test main BMAD parser orchestrator"""
    
    def test_parse_project_basic(self, tmp_path):
        """Test basic project parsing"""
        # Create minimal BMAD project structure
        bmad_output = tmp_path / "_bmad-output"
        impl_artifacts = bmad_output / "implementation-artifacts"
        impl_artifacts.mkdir(parents=True)
        
        # Create sprint-status.yaml
        sprint_status = impl_artifacts / "sprint-status.yaml"
        sprint_status.write_text("""project_name: Test Project
epics:
  - epic_id: 1
    title: Test Epic
    status: in-progress
    stories:
      - story_id: "1.1"
        story_key: "1-1-test-story"
        title: "Test Story"
        status: "ready-for-dev"
        epic: 1
""")
        
        # Create story file
        story_file = impl_artifacts / "1-1-test-story.md"
        story_file.write_text("""---
story_id: "1.1"
story_key: "1-1-test-story"
title: "Test Story"
status: "ready-for-dev"
epic: 1
---
# Test Story

## Tasks
- [ ] Task 1
- [x] Task 2
""")
        
        # Parse project
        parser = BMADParser(str(tmp_path))
        project = parser.parse_project()
        
        assert project is not None
        assert project.name == tmp_path.name
        assert project.phase == "Implementation"
        assert len(project.epics) == 1
        assert project.epics[0].title == "Test Epic"
        assert len(project.epics[0].stories) == 1
        assert project.epics[0].stories[0].title == "Test Story"
        assert len(project.epics[0].stories[0].tasks) == 2
    
    def test_parse_project_missing_files(self, tmp_path):
        """Test parsing project with missing story files"""
        bmad_output = tmp_path / "_bmad-output"
        impl_artifacts = bmad_output / "implementation-artifacts"
        impl_artifacts.mkdir(parents=True)
        
        # Create sprint-status pointing to non-existent story
        sprint_status = impl_artifacts / "sprint-status.yaml"
        sprint_status.write_text("""epics:
  - epic_id: 1
    title: Test Epic
    status: backlog
    stories:
      - story_id: "1.1"
        story_key: "1-1-missing-story"
        title: "Missing Story"
        status: "backlog"
        epic: 1
""")
        
        # Parse
        parser = BMADParser(str(tmp_path))
        project = parser.parse_project()
        
        # Should not crash, returns minimal story
        assert project is not None
        assert len(project.epics) == 1
        assert len(project.epics[0].stories) == 1
        assert project.epics[0].stories[0].title == "Missing Story"
        assert project.epics[0].stories[0].file_path == ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
