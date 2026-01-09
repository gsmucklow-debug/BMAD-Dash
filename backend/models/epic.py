"""
BMAD Dash - Epic Data Model
"""
from dataclasses import dataclass, field
from typing import List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from .story import Story


@dataclass
class Epic:
    """
    Represents a BMAD epic with its stories and progress tracking
    """
    epic_id: str  # "epic-1"
    title: str
    status: str  # "backlog" | "in-progress" | "done"
    stories: List['Story'] = field(default_factory=list)
    progress: Dict[str, int] = field(default_factory=lambda: {"total": 0, "done": 0})
    
    def to_dict(self) -> dict:
        """Serialize to dictionary for JSON responses"""
        return {
            "epic_id": self.epic_id,
            "title": self.title,
            "status": self.status,
            "stories": [story.to_dict() for story in self.stories],
            "progress": self.progress
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Epic':
        """Deserialize from dictionary"""
        from .story import Story
        return cls(
            epic_id=data.get("epic_id", ""),
            title=data.get("title", ""),
            status=data.get("status", "backlog"),
            stories=[Story.from_dict(s) for s in data.get("stories", [])],
            progress=data.get("progress", {"total": 0, "done": 0})
        )
