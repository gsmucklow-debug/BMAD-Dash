"""
BMAD Dash - Test Evidence Data Model
"""
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class TestEvidence:
    """
    Represents test evidence for a story
    """
    story_id: str
    test_files: List[str] = field(default_factory=list)
    pass_count: int = 0
    fail_count: int = 0
    failing_test_names: List[str] = field(default_factory=list)
    last_run_time: Optional[datetime] = None
    status: str = "unknown"  # "green", "yellow", "red", "unknown"
    
    @property
    def total_tests(self) -> int:
        """Total number of tests (passing + failing)"""
        return self.pass_count + self.fail_count
    
    def to_dict(self) -> dict:
        """Serialize to dictionary for JSON responses"""
        return {
            "story_id": self.story_id,
            "test_files": self.test_files,
            "pass_count": self.pass_count,
            "fail_count": self.fail_count,
            "total_tests": self.pass_count + self.fail_count,
            "failing_test_names": self.failing_test_names,
            "last_run_time": self.last_run_time.isoformat() if self.last_run_time else None,
            "status": self.status
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TestEvidence':
        """Deserialize from dictionary"""
        last_run_time = data.get("last_run_time")
        if isinstance(last_run_time, str):
            last_run_time = datetime.fromisoformat(last_run_time)
        
        return cls(
            story_id=data.get("story_id", ""),
            test_files=data.get("test_files", []),
            pass_count=data.get("pass_count", 0),
            fail_count=data.get("fail_count", 0),
            failing_test_names=data.get("failing_test_names", []),
            last_run_time=last_run_time,
            status=data.get("status", "unknown")
        )

