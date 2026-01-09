"""
BMAD Dash - Story Data Model
"""
from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .task import Task


@dataclass
class Story:
    """
    Represents a BMAD story with tasks and tracking metadata
    """
    story_id: str  # "1.1"
    story_key: str  # "1-1-bmad-artifact-parser-data-models"
    title: str
    status: str  # "backlog" | "ready-for-dev" | "in-progress" | "review" | "done"
    epic: int  # Epic number
    tasks: List['Task'] = field(default_factory=list)
    created: str = ""  # ISO date
    completed: Optional[str] = None  # ISO date if done
    file_path: str = ""
    mtime: float = 0.0
    
    def to_dict(self) -> dict:
        """Serialize to dictionary for JSON responses"""
        return {
            "story_id": self.story_id,
            "story_key": self.story_key,
            "title": self.title,
            "status": self.status,
            "epic": self.epic,
            "tasks": [task.to_dict() for task in self.tasks],
            "created": self.created,
            "completed": self.completed,
            "file_path": self.file_path,
            "mtime": self.mtime
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Story':
        """Deserialize from dictionary"""
        from .task import Task
        return cls(
            story_id=data.get("story_id", ""),
            story_key=data.get("story_key", ""),
            title=data.get("title", ""),
            status=data.get("status", "backlog"),
            epic=data.get("epic", 0),
            tasks=[Task.from_dict(t) for t in data.get("tasks", [])],
            created=data.get("created", ""),
            completed=data.get("completed"),
            file_path=data.get("file_path", ""),
            mtime=data.get("mtime", 0.0)
        )
