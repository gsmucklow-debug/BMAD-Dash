"""
BMAD Dash - Git Commit Correlation Service
Correlates Git commits to BMAD stories
"""
import re
import os
import logging
from typing import List, Tuple, Optional, Pattern
from datetime import datetime, timedelta
from git import Repo
from git.exc import InvalidGitRepositoryError, GitCommandError, NoSuchPathError
from backend.models.git_evidence import GitCommit


logger = logging.getLogger(__name__)

# Constants
MAX_COMMIT_AGE_DAYS = 7


class GitCorrelator:
    """
    Correlates Git commits to stories
    """
    
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.repo = None
        try:
            self.repo = Repo(repo_path)
            logger.info(f"GitCorrelator initialized for repo: {repo_path}")
        except (InvalidGitRepositoryError, GitCommandError, NoSuchPathError) as e:
            logger.error(f"Failed to initialize Git repository at {repo_path}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error initializing Git repository at {repo_path}: {e}")
    
    def get_commits_for_story(self, story_id: str) -> List[GitCommit]:
        """
        Gets Git commits related to a story
        
        Args:
            story_id: Story identifier (e.g., "1.3", "story-1.3")
            
        Returns:
            List of GitCommit objects matching the story
        """
        if not self.repo:
            logger.warning(f"No repository available for story {story_id}")
            return []
        
        try:
            # Build regex patterns for story matching
            patterns = self._build_story_patterns(story_id)
            
            # Find matching commits
            # Performance optimization: limit to 1000 commits to meet <100ms requirement
            # For repositories with >1000 commits, this ensures fast correlation
            matching_commits = []
            for commit in self.repo.iter_commits(max_count=1000):
                if self._matches_story(commit.message, patterns):
                    # Extract files changed
                    files_changed = list(commit.stats.files.keys()) if commit.stats.files else []
                    
                    git_commit = GitCommit(
                        sha=commit.hexsha,
                        message=commit.message.strip(),
                        author=commit.author.name,
                        timestamp=commit.committed_datetime,
                        files_changed=files_changed
                    )
                    matching_commits.append(git_commit)
            
            logger.info(f"Found {len(matching_commits)} commits for story {story_id}")
            return matching_commits
            
        except Exception as e:
            logger.error(f"Error getting commits for story {story_id}: {e}")
            return []
    
    def _build_story_patterns(self, story_id: str) -> List[Pattern]:
        """
        Build regex patterns to match story identifiers in commit messages
        
        Args:
            story_id: Story identifier (various formats accepted)
            
        Returns:
            List of compiled regex patterns
        """
        # Extract epic.story format (e.g., "1.3")
        normalized_id = self._extract_story_id(story_id)
        
        if not normalized_id:
            logger.warning(f"Could not extract story ID from: {story_id}")
            return []
        
        # Build patterns (case-insensitive)
        patterns = [
            re.compile(rf'story[-_\s]*{re.escape(normalized_id)}', re.IGNORECASE),  # story-1.3, story_1.3, story 1.3
            re.compile(rf'\[{re.escape(normalized_id)}\]', re.IGNORECASE),  # [1.3]
            re.compile(rf'(feat|fix|docs|style|refactor|test|chore)\(story[-_\s]*{re.escape(normalized_id)}\)', re.IGNORECASE),  # feat(story-1.3)
            re.compile(rf'(feat|fix|docs|style|refactor|test|chore)\({re.escape(normalized_id)}\)', re.IGNORECASE),  # feat(1.3)
        ]
        
        return patterns
    
    def _extract_story_id(self, story_id: str) -> Optional[str]:
        """
        Extract epic.story format from various input formats
        
        Args:
            story_id: Input in various formats (e.g., "1.3", "story-1.3", "1-3")
            
        Returns:
            Normalized format like "1.3" or None if invalid
        """
        # Already in epic.story format
        if re.match(r'^\d+\.\d+$', story_id):
            return story_id
        
        # Extract from "story-1.3" or "Story 1.3" format
        match = re.search(r'(\d+)[.\-_\s](\d+)', story_id)
        if match:
            return f"{match.group(1)}.{match.group(2)}"
        
        return None
    
    def _matches_story(self, commit_message: str, patterns: List[Pattern]) -> bool:
        """
        Check if commit message matches any of the story patterns
        
        Args:
            commit_message: Commit message to check
            patterns: List of compiled regex patterns
            
        Returns:
            True if message matches any pattern
        """
        if not commit_message:
            return False
        
        for pattern in patterns:
            if pattern.search(commit_message):
                logger.debug(f"Pattern matched in commit: {commit_message[:50]}...")
                return True
        
        return False
    
    def calculate_status(self, commits: List[GitCommit]) -> Tuple[str, Optional[datetime]]:
        """
        Calculate status based on commit recency
        
        Args:
            commits: List of GitCommit objects
            
        Returns:
            Tuple of (status, last_commit_time)
            Status: "green" (recent), "yellow" (old), "red" (none)
        """
        if not commits:
            return ("red", None)
        
        # Get most recent commit
        last_commit_time = self.get_last_commit_time(commits)
        
        if not last_commit_time:
            return ("red", None)
        
        # Calculate age (handle timezone-aware and naive datetimes)
        if last_commit_time.tzinfo is not None:
            # Timezone-aware: compare with timezone-aware now
            now = datetime.now(last_commit_time.tzinfo)
            age = now - last_commit_time
        else:
            # Naive datetime: compare with naive now
            age = datetime.now() - last_commit_time
        
        if age.days < MAX_COMMIT_AGE_DAYS:
            return ("green", last_commit_time)
        else:
            return ("yellow", last_commit_time)
    
    def get_last_commit_time(self, commits: List[GitCommit]) -> Optional[datetime]:
        """
        Get timestamp of most recent commit
        
        Args:
            commits: List of GitCommit objects
            
        Returns:
            Timestamp of most recent commit or None
        """
        if not commits:
            return None
        
        # Find most recent timestamp
        most_recent = max(commits, key=lambda c: c.timestamp)
        return most_recent.timestamp
    
    def get_commits_with_fallback(self, story_id: str, project_root: Optional[str] = None) -> List[GitCommit]:
        """
        Get commits for story with fallback to file modification time
        
        Args:
            story_id: Story identifier
            project_root: Optional project root path for fallback
            
        Returns:
            List of GitCommit objects (may include synthetic commit from file mtime)
        """
        # Try normal Git correlation first
        commits = self.get_commits_for_story(story_id)
        
        # If no commits and project_root provided, try file mtime fallback
        if not commits and project_root:
            logger.warning(f"No Git commits found for story {story_id}, attempting file mtime fallback")
            fallback_commit = self._create_fallback_commit(story_id, project_root)
            if fallback_commit:
                return [fallback_commit]
        
        return commits
    
    def _create_fallback_commit(self, story_id: str, project_root: str) -> Optional[GitCommit]:
        """
        Create synthetic commit from story file modification time
        
        Args:
            story_id: Story identifier
            project_root: Project root path
            
        Returns:
            GitCommit object or None if file not found
        """
        story_file_path = self._get_story_file_path(story_id, project_root)
        
        if not story_file_path or not os.path.exists(story_file_path):
            logger.warning(f"Story file not found for fallback: {story_file_path}")
            return None
        
        try:
            # Get file modification time
            mtime = os.path.getmtime(story_file_path)
            timestamp = datetime.fromtimestamp(mtime)
            
            # Create synthetic commit
            fallback_commit = GitCommit(
                sha="file-mtime",
                message=f"Fallback: File modification time for story {story_id}",
                author="System (File Timestamp)",
                timestamp=timestamp,
                files_changed=[story_file_path]
            )
            
            logger.info(f"Created fallback commit from file mtime for story {story_id}: {timestamp}")
            return fallback_commit
            
        except Exception as e:
            logger.error(f"Error creating fallback commit for story {story_id}: {e}")
            return None
    
    def _get_story_file_path(self, story_id: str, project_root: str) -> Optional[str]:
        """
        Get story file path from story ID
        
        Args:
            story_id: Story identifier (e.g., "1.3", "story-1.3")
            project_root: Project root path
            
        Returns:
            Story file path or None
        """
        # Normalize story_id to epic-story format (e.g., "1.3" -> "1-3")
        normalized = self._extract_story_id(story_id)
        if not normalized:
            return None
        
        # Convert "1.3" to "1-3" for filename
        story_key = normalized.replace('.', '-')
        
        # Common story file locations
        possible_paths = [
            os.path.join(project_root, "_bmad-output", "implementation-artifacts", f"{story_key}-*.md"),
            os.path.join(project_root, "_bmad-output", "implementation", f"{story_key}-*.md"),
            os.path.join(project_root, "stories", f"{story_key}-*.md"),
        ]
        
        # Try to find story file
        import glob
        for pattern in possible_paths:
            matches = glob.glob(pattern)
            if matches:
                return matches[0]  # Return first match
        
        return None
