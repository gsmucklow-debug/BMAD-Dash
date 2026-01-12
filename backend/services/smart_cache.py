"""
BMAD Dash - Smart Per-Project Cache Service
Story 5.55: Smart Per-Project Cache Layer - Selective Bootstrap & Persistence

This service provides intelligent caching for story evidence data:
- Stores cache in {project_root}/.bmad-cache/stories.json
- Uses file modification time (mtime) for invalidation
- Skips expensive git/test correlation for unchanged done stories
- Always refreshes in-progress stories for real-time accuracy
"""
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, Any, Tuple

logger = logging.getLogger(__name__)


class SmartCache:
    """
    Smart per-project cache for story evidence.
    
    Cache structure:
    {
        "metadata": {
            "project": "BMAD Dash",
            "cached_at": "2026-01-12T14:30:00Z",
            "cache_version": "1"
        },
        "stories": {
            "0.1": {
                "title": "...",
                "status": "done",
                "file_mtime": 1234567890,
                "evidence": {...},
                "cached_at": "2026-01-11T..."
            },
            "5.3": {
                "title": "...",
                "status": "in-progress",
                "file_mtime": 1234567890,
                "must_refresh": true
            }
        }
    }
    """
    
    CACHE_VERSION = "1"
    CACHE_DIR = ".bmad-cache"
    CACHE_FILE = "stories.json"
    
    # Statuses that should always be refreshed
    ACTIVE_STATUSES = ["in-progress", "review", "backlog", "todo", "ready-for-dev"]
    
    def __init__(self, project_root: str):
        """
        Initialize SmartCache for a project.
        
        Args:
            project_root: Path to the project root directory
        """
        self.project_root = Path(project_root)
        self.cache_dir = self.project_root / self.CACHE_DIR
        self.cache_file = self.cache_dir / self.CACHE_FILE
        self._cache_data: Optional[Dict[str, Any]] = None
        
    def _load_cache(self) -> Dict[str, Any]:
        """Load cache from disk, returning empty dict if missing or corrupted."""
        if not self.cache_file.exists():
            logger.debug(f"Cache file not found: {self.cache_file}")
            return self._empty_cache()
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Validate cache version
            if data.get("metadata", {}).get("cache_version") != self.CACHE_VERSION:
                logger.info("Cache version mismatch, clearing cache")
                return self._empty_cache()
                
            return data
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Error loading cache: {e}, using empty cache")
            return self._empty_cache()
    
    def _empty_cache(self) -> Dict[str, Any]:
        """Return an empty cache structure."""
        return {
            "metadata": {
                "project": self.project_root.name,
                "cached_at": datetime.now(timezone.utc).isoformat(),
                "cache_version": self.CACHE_VERSION
            },
            "stories": {}
        }
    
    def _save_cache(self, cache_data: Dict[str, Any]):
        """Save cache to disk with atomic write to prevent corruption."""
        try:
            # Ensure cache directory exists
            self.cache_dir.mkdir(parents=True, exist_ok=True)

            # Update metadata
            cache_data["metadata"]["cached_at"] = datetime.now(timezone.utc).isoformat()
            cache_data["metadata"]["project"] = self.project_root.name

            # Atomic write: write to temp file, then rename
            temp_file = self.cache_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)

            # Atomic rename (overwrites existing file)
            temp_file.replace(self.cache_file)

            logger.debug(f"Cache saved to {self.cache_file}")
        except IOError as e:
            logger.error(f"Error saving cache: {e}")
    
    def get_story_evidence(
        self,
        story_id: str,
        story_file_path: str,
        story_status: str
    ) -> Tuple[Optional[Dict[str, Any]], bool]:
        """
        Get cached evidence for a story if valid.
        
        Args:
            story_id: Story identifier (e.g., "5.4")
            story_file_path: Path to the story markdown file
            story_status: Current status of the story
            
        Returns:
            Tuple of (evidence_dict, cache_hit)
            - evidence_dict: Cached evidence if valid, None otherwise
            - cache_hit: True if cache was used, False if refresh needed
        """
        if not self._cache_data:
            self._cache_data = self._load_cache()
        
        # Always refresh active stories (in-progress, review, backlog, etc.)
        if story_status in self.ACTIVE_STATUSES:
            logger.debug(f"Story {story_id} has active status '{story_status}', forcing refresh")
            return None, False
        
        # Get cached story data
        stories = self._cache_data.get("stories", {})
        cached_story = stories.get(story_id)
        
        if not cached_story:
            logger.debug(f"Story {story_id} not in cache")
            return None, False
        
        # Check file modification time
        try:
            current_mtime = os.path.getmtime(story_file_path)
            cached_mtime = cached_story.get("file_mtime", 0)
            
            # Use small epsilon for float comparison (0.01s = 10ms tolerance)
            if abs(current_mtime - cached_mtime) < 0.01:
                # Cache hit - file hasn't changed
                logger.debug(f"Cache hit for story {story_id} (mtime matches)")
                return cached_story.get("evidence", {}), True
            else:
                # File changed - need refresh
                logger.debug(f"Story {story_id} file changed (mtime mismatch), forcing refresh")
                return None, False
                
        except OSError as e:
            logger.warning(f"Error getting mtime for {story_file_path}: {e}")
            return None, False
    
    def set_story_evidence(
        self,
        story_id: str,
        story_file_path: str,
        story_status: str,
        evidence: Dict[str, Any],
        title: str = ""
    ):
        """
        Store evidence for a story in the cache.
        
        Args:
            story_id: Story identifier
            story_file_path: Path to the story markdown file
            story_status: Current status of the story
            evidence: Evidence data to cache
            title: Story title (optional)
        """
        if not self._cache_data:
            self._cache_data = self._load_cache()
        
        try:
            file_mtime = os.path.getmtime(story_file_path)
        except OSError as e:
            logger.warning(f"Error getting mtime for {story_file_path}: {e}")
            file_mtime = 0
        
        # Store story cache entry
        self._cache_data["stories"][story_id] = {
            "title": title,
            "status": story_status,
            "file_mtime": file_mtime,
            "evidence": evidence,
            "cached_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Save to disk
        self._save_cache(self._cache_data)
    
    def invalidate_story(self, story_id: str):
        """
        Force a story to be refreshed on next load.
        
        Args:
            story_id: Story identifier to invalidate
        """
        if not self._cache_data:
            self._cache_data = self._load_cache()
        
        if story_id in self._cache_data.get("stories", {}):
            del self._cache_data["stories"][story_id]
            self._save_cache(self._cache_data)
            logger.info(f"Invalidated cache for story {story_id}")
    
    def clear_project_cache(self):
        """Clear all cached data for this project."""
        try:
            if self.cache_file.exists():
                self.cache_file.unlink()
                logger.info(f"Cleared cache file: {self.cache_file}")
            
            # Also clear the cache directory if empty
            if self.cache_dir.exists() and not any(self.cache_dir.iterdir()):
                self.cache_dir.rmdir()
                logger.info(f"Removed empty cache directory: {self.cache_dir}")
                
            self._cache_data = None
        except OSError as e:
            logger.error(f"Error clearing cache: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current cache.
        
        Returns:
            Dictionary with cache metadata and statistics
        """
        if not self._cache_data:
            self._cache_data = self._load_cache()
        
        stories = self._cache_data.get("stories", {})
        metadata = self._cache_data.get("metadata", {})
        
        # Count stories by status
        status_counts: Dict[str, int] = {}
        for story_data in stories.values():
            status = story_data.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Get cache age
        cached_at = metadata.get("cached_at")
        cache_age_ms = 0
        if cached_at:
            try:
                cached_dt = datetime.fromisoformat(cached_at.replace('Z', '+00:00'))
                age = datetime.now(timezone.utc) - cached_dt
                cache_age_ms = int(age.total_seconds() * 1000)
            except (ValueError, TypeError):
                pass
        
        return {
            "project": metadata.get("project", "Unknown"),
            "cache_version": metadata.get("cache_version", "unknown"),
            "total_stories": len(stories),
            "status_counts": status_counts,
            "cache_age_ms": cache_age_ms,
            "cache_file_exists": self.cache_file.exists()
        }
    
    def get_done_story_ids(self) -> list[str]:
        """
        Get list of story IDs that are marked as done in cache.
        
        Returns:
            List of story IDs with "done" status
        """
        if not self._cache_data:
            self._cache_data = self._load_cache()
        
        stories = self._cache_data.get("stories", {})
        return [
            story_id
            for story_id, data in stories.items()
            if data.get("status") == "done"
        ]
