"""
BMAD Dash - Git Evidence Data Models
"""
from dataclasses import dataclass, field
from typing import List
from datetime import datetime


@dataclass
class GitCommit:
    """
    Represents a Git commit
    """
    sha: str
    message: str
    author: str
    timestamp: datetime
    files_changed: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Serialize to dictionary for JSON responses"""
        return {
            "sha": self.sha,
            "message": self.message,
            "author": self.author,
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp,
            "files_changed": self.files_changed
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'GitCommit':
        """Deserialize from dictionary"""
        timestamp = data.get("timestamp", "")
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp)
            except ValueError:
                timestamp = datetime.now()
        return cls(
            sha=data.get("sha", ""),
            message=data.get("message", ""),
            author=data.get("author", ""),
            timestamp=timestamp,
            files_changed=data.get("files_changed", [])
        )


@dataclass
class GitEvidence:
    """
    Represents Git evidence for a story
    """
    story_id: str
    commits: List[GitCommit] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Serialize to dictionary for JSON responses"""
        return {
            "story_id": self.story_id,
            "commits": [commit.to_dict() for commit in self.commits]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'GitEvidence':
        """Deserialize from dictionary"""
        return cls(
            story_id=data.get("story_id", ""),
            commits=[GitCommit.from_dict(c) for c in data.get("commits", [])]
        )

