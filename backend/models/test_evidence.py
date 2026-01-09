"""
BMAD Dash - Test Evidence Data Model
"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class TestEvidence:
    """
    Represents test evidence for a story
    """
    story_id: str
    test_files: List[str] = field(default_factory=list)
    pass_count: int = 0
    fail_count: int = 0
    
    def to_dict(self) -> dict:
        """Serialize to dictionary for JSON responses"""
        return {
            "story_id": self.story_id,
            "test_files": self.test_files,
            "pass_count": self.pass_count,
            "fail_count": self.fail_count
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TestEvidence':
        """Deserialize from dictionary"""
        return cls(
            story_id=data.get("story_id", ""),
            test_files=data.get("test_files", []),
            pass_count=data.get("pass_count", 0),
            fail_count=data.get("fail_count", 0)
        )

