"""
BMAD Dash - In-Memory Cache with mtime Invalidation
"""
import os
from typing import Any, Optional
from datetime import datetime


class Cache:
    """
    Simple in-memory cache with file modification time tracking
    Automatically invalidates cached data when source files change
    """
    
    def __init__(self):
        self._cache = {}
        self._mtimes = {}
    
    def get(self, key: str, filepath: str = None) -> Optional[Any]:
        """
        Gets cached value if still valid
        
        Args:
            key: Cache key
            filepath: Optional filepath to check mtime for auto-invalidation
            
        Returns:
            Cached value if valid, None if cache miss or invalidated
        """
        # Check if key exists in cache
        if key not in self._cache:
            return None
        
        # If no filepath provided, return cached value
        if not filepath:
            return self._cache.get(key)
        
        # Check if file still exists
        if not os.path.exists(filepath):
            # File deleted, invalidate
            self.invalidate(key)
            return None
        
        # Check if file has been modified
        try:
            current_mtime = os.path.getmtime(filepath)
            cached_mtime = self._mtimes.get(key)
            
            if cached_mtime is None or current_mtime > cached_mtime:
                # File modified, invalidate
                self.invalidate(key)
                return None
            
            # Cache still valid
            return self._cache.get(key)
            
        except OSError:
            # Error accessing file, invalidate to be safe
            self.invalidate(key)
            return None
    
    def set(self, key: str, value: Any, filepath: str = None):
        """
        Sets cached value with optional filepath tracking
        
        Args:
            key: Cache key
            value: Value to cache
            filepath: Optional filepath to track mtime
        """
        self._cache[key] = value
        
        if filepath and os.path.exists(filepath):
            try:
                self._mtimes[key] = os.path.getmtime(filepath)
            except OSError:
                # If we can't get mtime, don't cache it
                pass
    
    def invalidate(self, key: str = None):
        """
        Invalidates cache entry or entire cache
        
        Args:
            key: Specific key to invalidate. If None, invalidates entire cache.
        """
        if key is None:
            # Invalidate entire cache
            self._cache.clear()
            self._mtimes.clear()
        else:
            # Invalidate specific key
            self._cache.pop(key, None)
            self._mtimes.pop(key, None)
    
    def invalidate_all(self):
        """Invalidates entire cache (alias for invalidate(None))"""
        self.invalidate(None)
    
    def size(self) -> int:
        """Returns number of cached items"""
        return len(self._cache)
    
    def keys(self) -> list:
        """Returns list of cached keys"""
        return list(self._cache.keys())

