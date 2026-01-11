
import pytest
from backend.models.project_state import ProjectState
from backend.models.story import Story
from backend.models.epic import Epic

def test_project_state_creation():
    """Test standard creation of ProjectState"""
    state = ProjectState(
        project={"name": "BMAD Dash", "bmad_version": "latest"},
        current={"story_id": "1.1"},
        epics={},
        stories={}
    )
    assert state.project["name"] == "BMAD Dash"
    assert state.version == "1.0"

def test_project_state_serialization():
    """Test JSON serialization"""
    state = ProjectState(
        project={"name": "test"},
        current={},
        epics={},
        stories={}
    )
    data = state.to_dict()
    assert "project" in data
    assert "current" in data
    assert "epics" in data
    assert "stories" in data
    assert "version" in data
    assert data["version"] == "1.0"

def test_project_state_deserialization():
    """Test JSON deserialization"""
    data = {
        "version": "1.0",
        "project": {"name": "test"},
        "current": {"story_id": "2.1"},
        "epics": {},
        "stories": {}
    }
    state = ProjectState.from_dict(data)
    assert state.project["name"] == "test"
    assert state.current["story_id"] == "2.1"
    assert state.version == "1.0"
