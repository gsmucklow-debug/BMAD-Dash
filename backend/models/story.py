"""
BMAD Dash - Story Data Model
"""
from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING, Dict, Any

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
    workflow_history: List[Dict[str, Any]] = field(default_factory=list)  # Workflow execution history
    gaps: List[Dict[str, Any]] = field(default_factory=list)  # Detected workflow gaps
    last_updated: Optional[str] = None  # ISO date from frontmatter
    evidence: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Serialize to dictionary for JSON responses"""
        # Calculate task stats
        total_tasks = len(self.tasks)
        done_tasks = sum(1 for t in self.tasks if t.status == "done")
        
        return {
            "story_id": self.story_id,
            "story_key": self.story_key,
            "title": self.title,
            "status": self.status,
            "epic": self.epic,
            "tasks": {
                "done": done_tasks,
                "total": total_tasks,
                "items": [task.to_dict() for task in self.tasks]
            },
            "evidence": self.evidence,
            "created": self.created,
            "completed": self.completed,
            "file_path": self.file_path,
            "mtime": self.mtime,
            "workflow_history": self.workflow_history,
            "gaps": self.gaps,
            "last_updated": self.last_updated
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Story':
        """Deserialize from dictionary"""
        from .task import Task
        
        tasks_data = data.get("tasks", [])
        if isinstance(tasks_data, dict):
            # Handle new object format
            tasks_list = tasks_data.get("items", [])
        else:
            # Handle legacy list format
            tasks_list = tasks_data

        return cls(
            story_id=data.get("story_id", ""),
            story_key=data.get("story_key", ""),
            title=data.get("title", ""),
            status=data.get("status", "backlog"),
            epic=data.get("epic", 0),
            tasks=[Task.from_dict(t) for t in tasks_list],
            evidence=data.get("evidence", {}),
            created=data.get("created", ""),
            completed=data.get("completed"),
            file_path=data.get("file_path", ""),
            mtime=data.get("mtime", 0.0),
            workflow_history=data.get("workflow_history", []),
            gaps=data.get("gaps", []),
            last_updated=data.get("last_updated")
        )
