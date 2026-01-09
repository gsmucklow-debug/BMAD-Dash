"""
BMAD Dash - Test File Discovery Service
Discovers and parses test files related to stories
"""
from typing import List


class TestDiscoverer:
    """
    Discovers test files for stories
    Will be fully implemented in Story 2.3
    """
    
    def __init__(self, project_path: str):
        self.project_path = project_path
    
    def discover_tests_for_story(self, story_id: str) -> List[str]:
        """
        Discovers test files related to a story
        Will be implemented in Story 2.3
        """
        raise NotImplementedError("Will be implemented in Story 2.3")
