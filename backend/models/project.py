"""
BMAD Dash - Project Data Model
"""
from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .epic import Epic


@dataclass
class Project:
    """
    Represents a BMAD project with its epics and current phase
    """
    name: str
    phase: str  # "Analysis" | "Planning" | "Solutioning" | "Implementation" | "Unknown"
    root_path: str
    epics: List['Epic'] = field(default_factory=list)
    sprint_status_mtime: float = 0.0
    
    def to_dict(self) -> dict:
        """Serialize to dictionary for JSON responses"""
        return {
            "name": self.name,
            "phase": self.phase,
            "root_path": self.root_path,
            "epics": [epic.to_dict() for epic in self.epics],
            "sprint_status_mtime": self.sprint_status_mtime
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Project':
        """Deserialize from dictionary"""
        from .epic import Epic
        return cls(
            name=data.get("name", ""),
            phase=data.get("phase", "Unknown"),
            root_path=data.get("root_path", ""),
            epics=[Epic.from_dict(e) for e in data.get("epics", [])],
            sprint_status_mtime=data.get("sprint_status_mtime", 0.0)
        )
