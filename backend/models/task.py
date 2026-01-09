"""
BMAD Dash - Task Data Model
"""
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Task:
    """
    Represents a BMAD task with optional subtasks
    """
    task_id: str
    title: str
    status: str  # "todo" | "done"
    subtasks: List[Dict[str, str]] = field(default_factory=list)  # [{"text": "...", "status": "done"}]
    
    def to_dict(self) -> dict:
        """Serialize to dictionary for JSON responses"""
        return {
            "task_id": self.task_id,
            "title": self.title,
            "status": self.status,
            "subtasks": self.subtasks
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        """Deserialize from dictionary"""
        return cls(
            task_id=data.get("task_id", ""),
            title=data.get("title", ""),
            status=data.get("status", "todo"),
            subtasks=data.get("subtasks", [])
        )

