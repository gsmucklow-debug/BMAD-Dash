"""
BMAD Dash - Cache Tests
Tests for cache system with mtime invalidation
"""
import pytest
import os
import tempfile
import time
from backend.utils.cache import Cache


class TestCache:
    """Test Cache functionality"""
    
    def test_cache_set_and_get(self):
        """Test basic cache set and get"""
        cache = Cache()
        
        cache.set("key1", "value1")
        result = cache.get("key1")
        
        assert result == "value1"
    
    def test_cache_miss(self):
        """Test cache miss returns None"""
        cache = Cache()
        
        result = cache.get("nonexistent")
        
        assert result is None
    
    def test_cache_with_filepath_tracking(self, tmp_path):
        """Test cache with file modification time tracking"""
        cache = Cache()
        
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("original content")
        
        # Cache value with filepath
        cache.set("key1", "cached_value", str(test_file))
        
        # Retrieve from cache (should hit)
        result = cache.get("key1", str(test_file))
        assert result == "cached_value"
    
    def test_cache_invalidation_on_file_change(self, tmp_path):
        """Test cache invalidates when file is modified"""
        cache = Cache()
        
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("original")
        
        # Cache value
        cache.set("key1", "original_cache", str(test_file))
        
        # Verify cache hit
        assert cache.get("key1", str(test_file)) == "original_cache"
        
        # Wait a bit to ensure mtime changes
        time.sleep(0.1)
        
        # Modify file
        test_file.write_text("modified")
        
        # Cache should be invalidated
        result = cache.get("key1", str(test_file))
        assert result is None
    
    def test_cache_invalidation_on_file_deletion(self, tmp_path):
        """Test cache invalidates when file is deleted"""
        cache = Cache()
        
        # Create and cache
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        cache.set("key1", "value", str(test_file))
        
        # Delete file
        test_file.unlink()
        
        # Should return None
        result = cache.get("key1", str(test_file))
        assert result is None
    
    def test_cache_without_filepath(self):
        """Test cache get without filepath tracking"""
        cache = Cache()
        
        cache.set("key1", "value1")
        
        # Get without filepath should return cached value
        result = cache.get("key1")
        assert result == "value1"
    
    def test_invalidate_specific_key(self):
        """Test invalidating a specific cache key"""
        cache = Cache()
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        # Invalidate key1
        cache.invalidate("key1")
        
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
    
    def test_invalidate_all(self):
        """Test invalidating entire cache"""
        cache = Cache()
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        
        # Invalidate all
        cache.invalidate_all()
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert cache.get("key3") is None
        assert cache.size() == 0
    
    def test_invalidate_with_none(self):
        """Test invalidate(None) clears entire cache"""
        cache = Cache()
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        cache.invalidate(None)
        
        assert cache.size() == 0
    
    def test_cache_size(self):
        """Test cache size tracking"""
        cache = Cache()
        
        assert cache.size() == 0
        
        cache.set("key1", "value1")
        assert cache.size() == 1
        
        cache.set("key2", "value2")
        assert cache.size() == 2
        
        cache.invalidate("key1")
        assert cache.size() == 1
    
    def test_cache_keys(self):
        """Test getting list of cached keys"""
        cache = Cache()
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        
        keys = cache.keys()
        
        assert len(keys) == 3
        assert "key1" in keys
        assert "key2" in keys
        assert "key3" in keys
    
    def test_cache_handles_complex_objects(self):
        """Test caching complex objects"""
        cache = Cache()
        
        complex_obj = {
            "nested": {
                "data": [1, 2, 3],
                "more": {"deep": "value"}
            },
            "list": ["a", "b", "c"]
        }
        
        cache.set("complex", complex_obj)
        result = cache.get("complex")
        
        assert result == complex_obj
        assert result['nested']['data'] == [1, 2, 3]
        assert result['list'] == ["a", "b", "c"]
    
    def test_cache_error_handling_invalid_filepath(self):
        """Test cache handles invalid filepath gracefully"""
        cache = Cache()
        
        # Set with invalid filepath
        cache.set("key1", "value", "/nonexistent/path/file.txt")
        
        # Should still be able to get without filepath
        assert cache.get("key1") == "value"
    
    def test_multiple_files_different_keys(self, tmp_path):
        """Test caching multiple files with different keys"""
        cache = Cache()
        
        # Create multiple files
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("content1")
        file2.write_text("content2")
        
        # Cache them
        cache.set("key1", "data1", str(file1))
        cache.set("key2", "data2", str(file2))
        
        # Verify both cached
        assert cache.get("key1", str(file1)) == "data1"
        assert cache.get("key2", str(file2)) == "data2"
        
        # Modify file1
        time.sleep(0.1)
        file1.write_text("modified1")
        
        # Only key1 should be invalidated
        assert cache.get("key1", str(file1)) is None
        assert cache.get("key2", str(file2)) == "data2"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
