"""
BMAD Dash - Git Commit Correlation Service
Correlates Git commits to BMAD stories
"""
from typing import List


class GitCorrelator:
    """
    Correlates Git commits to stories
    Will be fully implemented in Story 2.2
    """
    
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
    
    def get_commits_for_story(self, story_id: str) -> List[dict]:
        """
        Gets Git commits related to a story
        Will be implemented in Story 2.2
        """
        raise NotImplementedError("Will be implemented in Story 2.2")
