"""
BMAD Dash - SmartCache Tests
Story 5.55: Smart Per-Project Cache Layer
Unit tests for SmartCache service
"""

import json
import os
import tempfile
import time
import unittest
from pathlib import Path

from backend.services.smart_cache import SmartCache


class TestSmartCache(unittest.TestCase):
    """Test cases for SmartCache service"""
    
    def setUp(self):
        """Set up temporary directory for each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        self.smart_cache = SmartCache(str(self.project_root))
    
    def tearDown(self):
        """Clean up temporary directory after each test"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_cache_file_structure(self):
        """Test that cache file is created with correct structure"""
        # Set some evidence
        self.smart_cache.set_story_evidence(
            "1.1",
            str(self.project_root / "story.md"),
            "done",
            {"commits": 5, "tests_passed": 10},
            "Test Story"
        )
        
        # Check cache file exists
        cache_file = self.project_root / ".bmad-cache" / "stories.json"
        self.assertTrue(cache_file.exists())
        
        # Check cache structure
        with open(cache_file, 'r') as f:
            cache_data = json.load(f)
        
        self.assertIn("metadata", cache_data)
        self.assertIn("stories", cache_data)
        self.assertIn("1.1", cache_data["stories"])
        self.assertEqual(cache_data["metadata"]["cache_version"], "1")
    
    def test_get_story_evidence_cache_hit(self):
        """Test cache hit when story file hasn't changed"""
        # Create a test story file
        story_file = self.project_root / "story.md"
        story_file.write_text("# Test Story")
        file_mtime = os.path.getmtime(story_file)
        
        # Set evidence in cache
        evidence = {"commits": 5, "tests_passed": 10}
        self.smart_cache.set_story_evidence(
            "1.1",
            str(story_file),
            "done",
            evidence,
            "Test Story"
        )
        
        # Get evidence - should be cache hit
        cached_evidence, cache_hit = self.smart_cache.get_story_evidence(
            "1.1",
            str(story_file),
            "done"
        )
        
        self.assertTrue(cache_hit)
        self.assertEqual(cached_evidence, evidence)
    
    def test_get_story_evidence_cache_miss_mtime_changed(self):
        """Test cache miss when story file modification time changes"""
        # Create a test story file
        story_file = self.project_root / "story.md"
        story_file.write_text("# Test Story")
        
        # Set evidence in cache
        evidence = {"commits": 5, "tests_passed": 10}
        self.smart_cache.set_story_evidence(
            "1.1",
            str(story_file),
            "done",
            evidence,
            "Test Story"
        )
        
        # Wait longer for file system to update mtime
        time.sleep(1.0)
        story_file.write_text("# Modified Story")
        
        # Force file system flush
        os.sync() if hasattr(os, 'sync') else None
        
        # Get evidence - should be cache miss
        cached_evidence, cache_hit = self.smart_cache.get_story_evidence(
            "1.1",
            str(story_file),
            "done"
        )
        
        self.assertFalse(cache_hit)
        self.assertIsNone(cached_evidence)
    
    def test_active_status_always_refreshes(self):
        """Test that active status stories always refresh (no cache)"""
        # Create a test story file
        story_file = self.project_root / "story.md"
        story_file.write_text("# Test Story")
        
        # Set evidence in cache
        evidence = {"commits": 5, "tests_passed": 10}
        self.smart_cache.set_story_evidence(
            "1.1",
            str(story_file),
            "in-progress",
            evidence,
            "Test Story"
        )
        
        # Get evidence for in-progress story - should be cache miss
        cached_evidence, cache_hit = self.smart_cache.get_story_evidence(
            "1.1",
            str(story_file),
            "in-progress"
        )
        
        self.assertFalse(cache_hit)
        self.assertIsNone(cached_evidence)
    
    def test_review_status_always_refreshes(self):
        """Test that review status stories always refresh (no cache)"""
        # Create a test story file
        story_file = self.project_root / "story.md"
        story_file.write_text("# Test Story")
        
        # Set evidence in cache
        evidence = {"commits": 5, "tests_passed": 10}
        self.smart_cache.set_story_evidence(
            "1.1",
            str(story_file),
            "review",
            evidence,
            "Test Story"
        )
        
        # Get evidence for review story - should be cache miss
        cached_evidence, cache_hit = self.smart_cache.get_story_evidence(
            "1.1",
            str(story_file),
            "review"
        )
        
        self.assertFalse(cache_hit)
        self.assertIsNone(cached_evidence)
    
    def test_invalidate_story(self):
        """Test invalidating a specific story cache entry"""
        # Create a test story file
        story_file = self.project_root / "story.md"
        story_file.write_text("# Test Story")
        
        # Set evidence in cache
        evidence = {"commits": 5, "tests_passed": 10}
        self.smart_cache.set_story_evidence(
            "1.1",
            str(story_file),
            "done",
            evidence,
            "Test Story"
        )
        
        # Invalidate story
        self.smart_cache.invalidate_story("1.1")
        
        # Get evidence - should be cache miss
        cached_evidence, cache_hit = self.smart_cache.get_story_evidence(
            "1.1",
            str(story_file),
            "done"
        )
        
        self.assertFalse(cache_hit)
        self.assertIsNone(cached_evidence)
    
    def test_clear_project_cache(self):
        """Test clearing all cache data for a project"""
        # Create test story files and set evidence
        for i in range(3):
            story_file = self.project_root / f"story{i}.md"
            story_file.write_text(f"# Test Story {i}")
            self.smart_cache.set_story_evidence(
                f"1.{i+1}",
                str(story_file),
                "done",
                {"commits": i},
                f"Test Story {i}"
            )
        
        # Clear cache
        self.smart_cache.clear_project_cache()
        
        # Check cache file is deleted
        cache_file = self.project_root / ".bmad-cache" / "stories.json"
        self.assertFalse(cache_file.exists())
    
    def test_get_cache_stats(self):
        """Test getting cache statistics"""
        # Create test stories with different statuses
        for i in range(3):
            status = "done" if i < 2 else "in-progress"
            story_file = self.project_root / f"story{i}.md"
            story_file.write_text(f"# Test Story {i}")
            self.smart_cache.set_story_evidence(
                f"1.{i+1}",
                str(story_file),
                status,
                {"commits": i},
                f"Test Story {i}"
            )
        
        # Get stats
        stats = self.smart_cache.get_cache_stats()
        
        self.assertEqual(stats["total_stories"], 3)
        self.assertEqual(stats["status_counts"]["done"], 2)
        self.assertEqual(stats["status_counts"]["in-progress"], 1)
        self.assertTrue(stats["cache_file_exists"])
        # Note: cache_age_ms might be 0 on fast systems, just verify it's a number
        self.assertIsInstance(stats["cache_age_ms"], int)
        self.assertGreaterEqual(stats["cache_age_ms"], 0)
    
    def test_get_done_story_ids(self):
        """Test getting list of done story IDs from cache"""
        # Create test stories with different statuses
        story_ids = []
        for i in range(5):
            status = "done" if i % 2 == 0 else "in-progress"
            story_id = f"1.{i+1}"
            story_ids.append(story_id)
            story_file = self.project_root / f"story{i}.md"
            story_file.write_text(f"# Test Story {i}")
            self.smart_cache.set_story_evidence(
                story_id,
                str(story_file),
                status,
                {"commits": i},
                f"Test Story {i}"
            )
        
        # Get done story IDs
        done_ids = self.smart_cache.get_done_story_ids()
        
        # Should have 3 done stories (1.1, 1.3, 1.5)
        self.assertEqual(len(done_ids), 3)
        self.assertIn("1.1", done_ids)
        self.assertIn("1.3", done_ids)
        self.assertIn("1.5", done_ids)
        self.assertNotIn("1.2", done_ids)
        self.assertNotIn("1.4", done_ids)
    
    def test_multi_project_isolation(self):
        """Test that different projects have isolated caches"""
        # Create two project roots
        project1 = Path(tempfile.mkdtemp())
        project2 = Path(tempfile.mkdtemp())
        
        try:
            cache1 = SmartCache(str(project1))
            cache2 = SmartCache(str(project2))
            
            # Set different evidence in each project
            story_file1 = project1 / "story.md"
            story_file1.write_text("# Project 1 Story")
            cache1.set_story_evidence(
                "1.1",
                str(story_file1),
                "done",
                {"project": 1},
                "Project 1 Story"
            )
            
            story_file2 = project2 / "story.md"
            story_file2.write_text("# Project 2 Story")
            cache2.set_story_evidence(
                "1.1",
                str(story_file2),
                "done",
                {"project": 2},
                "Project 2 Story"
            )
            
            # Get stats from each project
            stats1 = cache1.get_cache_stats()
            stats2 = cache2.get_cache_stats()
            
            # Each should have different project names
            self.assertEqual(stats1["total_stories"], 1)
            self.assertEqual(stats2["total_stories"], 1)
            # Note: get_cache_stats() returns summary stats, not full cache data
            # Verify project names are different instead
            self.assertNotEqual(stats1["project"], stats2["project"])
            
        finally:
            import shutil
            if os.path.exists(project1):
                shutil.rmtree(project1)
            if os.path.exists(project2):
                shutil.rmtree(project2)
    
    def test_cache_version_mismatch_clears_cache(self):
        """Test that cache version mismatch results in empty cache"""
        # Create cache file with old version
        cache_dir = self.project_root / ".bmad-cache"
        cache_dir.mkdir(parents=True)
        cache_file = cache_dir / "stories.json"
        
        old_cache_data = {
            "metadata": {
                "project": "Test",
                "cached_at": "2026-01-01T00:00:00Z",
                "cache_version": "0"  # Old version
            },
            "stories": {
                "1.1": {
                    "title": "Old Story",
                    "status": "done",
                    "file_mtime": 1234567890,
                    "evidence": {"old": True}
                }
            }
        }
        
        with open(cache_file, 'w') as f:
            json.dump(old_cache_data, f)
        
        # Create new SmartCache instance - should detect version mismatch
        new_cache = SmartCache(str(self.project_root))
        
        # Try to get evidence - should return None (cache miss)
        cached_evidence, cache_hit = new_cache.get_story_evidence(
            "1.1",
            str(self.project_root / "story.md"),
            "done"
        )
        
        self.assertFalse(cache_hit)
        self.assertIsNone(cached_evidence)


if __name__ == '__main__':
    unittest.main()
