"""
BMAD Dash - Project State Model
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Union
from .epic import Epic
from .story import Story

@dataclass
class ProjectState:
    """
    Root model for project-state.json.
    Acts as the source of truth for the AI Coach and Dashboard cache.
    """
    project: Dict[str, Any]
    current: Dict[str, Any]
    epics: Dict[str, Epic] = field(default_factory=dict)
    stories: Dict[str, Story] = field(default_factory=dict)
    version: str = "1.0"
    workflow_validation: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize complete project state to dictionary"""
        return {
            "version": self.version,
            "project": self.project,
            "current": self.current,
            "epics": {k: v.to_dict() if hasattr(v, 'to_dict') else v for k, v in self.epics.items()},
            "stories": {k: v.to_dict() if hasattr(v, 'to_dict') else v for k, v in self.stories.items()},
            "workflow_validation": self.workflow_validation
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectState':
        """Deserialize from dictionary"""
        epics_data = data.get("epics", {})
        stories_data = data.get("stories", {})
        
        # safely handle if epics are already objects or dicts
        epics = {}
        for k, v in epics_data.items():
            if isinstance(v, dict):
                epics[k] = Epic.from_dict(v)
            else:
                epics[k] = v
                
        stories = {}
        for k, v in stories_data.items():
            if isinstance(v, dict):
                stories[k] = Story.from_dict(v)
            else:
                stories[k] = v

        return cls(
            project=data.get("project", {}),
            current=data.get("current", {}),
            epics=epics,
            stories=stories,
            version=data.get("version", "1.0"),
            workflow_validation=data.get("workflow_validation", {})
        )
