import pytest
import os
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
from datetime import datetime
from backend.services.project_state_cache import ProjectStateCache
from backend.models.project_state import ProjectState
from backend.models.story import Story
from backend.models.epic import Epic

CACHE_FILE = "test_project_state.json"

@pytest.fixture
def cache_service(tmp_path):
    cache_path = tmp_path / CACHE_FILE
    return ProjectStateCache(str(cache_path))

def test_cache_load_missing(cache_service):
    """Test loading when cache missing - should initialize empty/default"""
    state = cache_service.load()
    assert isinstance(state, ProjectState)
    assert state.version == "1.0"
    assert Path(cache_service.cache_file).exists()

def test_cache_save_load(cache_service):
    """Test saving and loading data"""
    state = ProjectState(
        project={"name": "Test"},
        current={},
        epics={},
        stories={'1.1': Story(story_id='1.1', story_key='1-1-test', title='Test Story', status='done', epic=1)}
    )
    cache_service.cache_data = state
    cache_service.save()
    
    new_service = ProjectStateCache(cache_service.cache_file)
    loaded = new_service.load()
    assert loaded.project["name"] == "Test"
    assert "1.1" in loaded.stories
    assert loaded.stories["1.1"].title == "Test Story"

def test_get_story(cache_service):
    """Test get_story method"""
    state = ProjectState(
        project={}, current={}, epics={},
        stories={'1.1': Story(story_id='1.1', story_key='key', title='Title', status='done', epic=1)}
    )
    cache_service.cache_data = state
    story = cache_service.get_story("1.1")
    assert story is not None
    assert story.title == "Title"
    assert cache_service.get_story("9.9") is None

def test_update_story(cache_service):
    """Test update_story method"""
    state = ProjectState(
        project={}, current={}, epics={},
        stories={'1.1': Story(story_id='1.1', story_key='key', title='Old Title', status='done', epic=1)}
    )
    cache_service.cache_data = state
    
    updated_data = {"title": "New Title", "status": "in-progress"}
    cache_service.update_story("1.1", updated_data)
    
    story = cache_service.get_story("1.1")
    assert story.title == "New Title"
    assert story.status == "in-progress"

def test_bootstrap(cache_service):
    """Test bootstrap functionality with mocks"""
    with patch('backend.parsers.bmad_parser.BMADParser') as mock_parser_cls, \
         patch('backend.services.git_correlator.GitCorrelator') as mock_git_cls, \
         patch('backend.services.test_discoverer.TestDiscoverer') as mock_test_cls:
        
        mock_parser = mock_parser_cls.return_value
        mock_git = mock_git_cls.return_value
        mock_test = mock_test_cls.return_value
        
        mock_project = MagicMock()
        mock_project.name = "Test Project"
        mock_project.phase = "Dev"
        story = Story(story_id="1.1", story_key="1-1-test", title="Story 1", status="done", epic=1)
        # Note: epics must be iterable
        mock_project.epics = [
            Epic(epic_id="epic-1", title="Epic 1", status="in-progress", stories=[story])
        ]
        mock_parser.parse_project.return_value = mock_project
        
        mock_commit = MagicMock()
        mock_commit.timestamp = datetime(2026, 1, 1)
        mock_git.get_commits_for_story.return_value = [mock_commit]
        
        mock_test_ev = MagicMock()
        mock_test_ev.pass_count = 10
        mock_test_ev.fail_count = 0
        mock_test_ev.last_run_time = datetime(2026, 1, 1)
        mock_test.get_test_evidence_for_story.return_value = mock_test_ev
        
        state = cache_service.bootstrap(project_root=".")
        
        assert state is not None
        assert "epic-1" in state.epics
        assert "1.1" in state.stories
        assert state.stories["1.1"].evidence["commits"] == 1
        # Check last_commit format
        assert state.stories["1.1"].evidence["last_commit"] == "2026-01-01T00:00:00"
        assert state.stories["1.1"].evidence["tests_passed"] == 10
