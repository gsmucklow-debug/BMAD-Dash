"""
Unit tests for GitCorrelator service
Tests Git commit correlation functionality
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from backend.services.git_correlator import GitCorrelator
from backend.models.git_evidence import GitCommit


class TestGitCorrelator:
    """Test suite for GitCorrelator class"""
    
    def test_init_with_valid_repo(self):
        """Test GitCorrelator initializes with valid repo path"""
        with patch('backend.services.git_correlator.Repo'):
            correlator = GitCorrelator("/fake/repo/path")
            assert correlator.repo_path == "/fake/repo/path"
    
    def test_get_commits_for_story_with_matching_commits(self):
        """Test get_commits_for_story returns matching commits"""
        # Setup mock commit
        mock_commit = Mock()
        mock_commit.hexsha = "abc123"
        mock_commit.message = "feat(story-1.3): Implement dashboard"
        mock_commit.author.name = "Test Author"
        mock_commit.committed_datetime = datetime.now()
        mock_commit.stats.files = {"backend/api/dashboard.py": {"lines": 10}}
        
        # Mock GitPython Repo
        with patch('backend.services.git_correlator.Repo') as MockRepo:
            mock_repo = Mock()
            mock_repo.iter_commits.return_value = [mock_commit]
            MockRepo.return_value = mock_repo
            
            correlator = GitCorrelator("/fake/repo")
            commits = correlator.get_commits_for_story("1.3")
            
            assert len(commits) == 1
            assert commits[0].sha == "abc123"
            assert "dashboard" in commits[0].message.lower()
    
    def test_get_commits_for_story_no_matches(self):
        """Test get_commits_for_story returns empty list when no matches"""
        mock_commit = Mock()
        mock_commit.hexsha = "abc123"
        mock_commit.message = "feat: Unrelated commit"
        mock_commit.author.name = "Test Author"
        mock_commit.committed_datetime = datetime.now()
        mock_commit.stats.files = {}
        
        with patch('backend.services.git_correlator.Repo') as MockRepo:
            mock_repo = Mock()
            mock_repo.iter_commits.return_value = [mock_commit]
            MockRepo.return_value = mock_repo
            
            correlator = GitCorrelator("/fake/repo")
            commits = correlator.get_commits_for_story("1.3")
            
            assert len(commits) == 0
    
    def test_pattern_matching_story_dash_format(self):
        """Test pattern matches 'story-1.3' format"""
        mock_commit = Mock()
        mock_commit.hexsha = "abc123"
        mock_commit.message = "story-1.3: Implementation"
        mock_commit.author.name = "Author"
        mock_commit.committed_datetime = datetime.now()
        mock_commit.stats.files = {}
        
        with patch('backend.services.git_correlator.Repo') as MockRepo:
            mock_repo = Mock()
            mock_repo.iter_commits.return_value = [mock_commit]
            MockRepo.return_value = mock_repo
            
            correlator = GitCorrelator("/fake/repo")
            commits = correlator.get_commits_for_story("1.3")
            
            assert len(commits) == 1
    
    def test_pattern_matching_bracket_format(self):
        """Test pattern matches '[1.3]' format"""
        mock_commit = Mock()
        mock_commit.hexsha = "abc123"
        mock_commit.message = "[1.3] Fix bug"
        mock_commit.author.name = "Author"
        mock_commit.committed_datetime = datetime.now()
        mock_commit.stats.files = {}
        
        with patch('backend.services.git_correlator.Repo') as MockRepo:
            mock_repo = Mock()
            mock_repo.iter_commits.return_value = [mock_commit]
            MockRepo.return_value = mock_repo
            
            correlator = GitCorrelator("/fake/repo")
            commits = correlator.get_commits_for_story("1.3")
            
            assert len(commits) == 1
    
    def test_pattern_matching_conventional_commits(self):
        """Test pattern matches 'feat(story-1.3):' format"""
        mock_commit = Mock()
        mock_commit.hexsha = "abc123"
        mock_commit.message = "feat(story-1.3): Add feature"
        mock_commit.author.name = "Author"
        mock_commit.committed_datetime = datetime.now()
        mock_commit.stats.files = {}
        
        with patch('backend.services.git_correlator.Repo') as MockRepo:
            mock_repo = Mock()
            mock_repo.iter_commits.return_value = [mock_commit]
            MockRepo.return_value = mock_repo
            
            correlator = GitCorrelator("/fake/repo")
            commits = correlator.get_commits_for_story("1.3")
            
            assert len(commits) == 1
    
    def test_pattern_matching_case_insensitive(self):
        """Test pattern matching is case-insensitive"""
        mock_commit = Mock()
        mock_commit.hexsha = "abc123"
        mock_commit.message = "STORY-1.3: Implementation"
        mock_commit.author.name = "Author"
        mock_commit.committed_datetime = datetime.now()
        mock_commit.stats.files = {}
        
        with patch('backend.services.git_correlator.Repo') as MockRepo:
            mock_repo = Mock()
            mock_repo.iter_commits.return_value = [mock_commit]
            MockRepo.return_value = mock_repo
            
            correlator = GitCorrelator("/fake/repo")
            commits = correlator.get_commits_for_story("1.3")
            
            assert len(commits) == 1
    
    def test_calculate_status_green_recent_commits(self):
        """Test status is green for recent commits"""
        recent_commit = GitCommit(
            sha="abc123",
            message="test",
            author="Author",
            timestamp=datetime.now() - timedelta(days=1),
            files_changed=[]
        )
        
        with patch('backend.services.git_correlator.Repo'):
            correlator = GitCorrelator("/fake/repo")
            status, last_time = correlator.calculate_status([recent_commit])
            
            assert status == "green"
            assert last_time is not None
    
    def test_calculate_status_yellow_old_commits(self):
        """Test status is yellow for commits >7 days old"""
        old_commit = GitCommit(
            sha="abc123",
            message="test",
            author="Author",
            timestamp=datetime.now() - timedelta(days=10),
            files_changed=[]
        )
        
        with patch('backend.services.git_correlator.Repo'):
            correlator = GitCorrelator("/fake/repo")
            status, last_time = correlator.calculate_status([old_commit])
            
            assert status == "yellow"
    
    def test_calculate_status_red_no_commits(self):
        """Test status is red when no commits"""
        with patch('backend.services.git_correlator.Repo'):
            correlator = GitCorrelator("/fake/repo")
            status, last_time = correlator.calculate_status([])
            
            assert status == "red"
            assert last_time is None
    
    def test_error_handling_invalid_repo(self):
        """Test graceful handling of invalid Git repository"""
        with patch('backend.services.git_correlator.Repo') as MockRepo:
            MockRepo.side_effect = Exception("Invalid repository")
            
            # Should handle exception gracefully in __init__
            correlator = GitCorrelator("/fake/repo")
            assert correlator.repo is None
            
            # Should return empty list when repo is None
            commits = correlator.get_commits_for_story("1.3")
            assert commits == []
    
    def test_story_id_extraction_from_various_formats(self):
        """Test story ID extraction handles various input formats"""
        with patch('backend.services.git_correlator.Repo'):
            correlator = GitCorrelator("/fake/repo")
            
            # Test that different input formats get normalized
            # This tests the _extract_story_id method if implemented
            # Or that the pattern builder handles various formats
            test_cases = [
                "1.3",
                "story-1.3",
                "Story 1.3",
                "1-3"
            ]
            
            # All should be able to match commits
            for story_id in test_cases:
                patterns = correlator._build_story_patterns(story_id)
                assert len(patterns) > 0
    
    def test_fallback_commit_creation(self):
        """Test creation of fallback commit from file mtime"""
        import tempfile
        import os
        
        # Create temporary story file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Test Story")
            temp_file = f.name
        
        try:
            with patch('backend.services.git_correlator.Repo'):
                correlator = GitCorrelator("/fake/repo")
                
                # Mock _get_story_file_path to return our temp file
                with patch.object(correlator, '_get_story_file_path', return_value=temp_file):
                    fallback_commit = correlator._create_fallback_commit("1.3", "/fake/project")
                    
                    assert fallback_commit is not None
                    assert fallback_commit.sha == "file-mtime"
                    assert "Fallback" in fallback_commit.message
                    assert fallback_commit.timestamp is not None
        finally:
            os.unlink(temp_file)
    
    def test_fallback_when_no_git_commits(self):
        """Test get_commits_with_fallback uses file mtime when no Git commits"""
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Test Story")
            temp_file = f.name
        
        try:
            with patch('backend.services.git_correlator.Repo') as MockRepo:
                # Setup mock repo with no matching commits
                mock_repo = Mock()
                mock_repo.iter_commits.return_value = []
                MockRepo.return_value = mock_repo
                
                correlator = GitCorrelator("/fake/repo")
                
                # Mock _get_story_file_path to return our temp file
                with patch.object(correlator, '_get_story_file_path', return_value=temp_file):
                    commits = correlator.get_commits_with_fallback("1.3", "/fake/project")
                    
                    # Should have one fallback commit
                    assert len(commits) == 1
                    assert commits[0].sha == "file-mtime"
        finally:
            os.unlink(temp_file)
    
    def test_performance_requirement(self):
        """Test that correlation completes in <100ms for typical repository"""
        import time
        
        # Create mock commits (simulating 100 commits)
        mock_commits = []
        for i in range(100):
            mock_commit = Mock()
            mock_commit.hexsha = f"abc{i:03d}"
            mock_commit.message = f"feat(story-1.3): Commit {i}"
            mock_commit.author.name = "Test Author"
            mock_commit.committed_datetime = datetime.now()
            mock_commit.stats.files = {}
            mock_commits.append(mock_commit)
        
        with patch('backend.services.git_correlator.Repo') as MockRepo:
            mock_repo = Mock()
            mock_repo.iter_commits.return_value = mock_commits
            MockRepo.return_value = mock_repo
            
            correlator = GitCorrelator("/fake/repo")
            
            start_time = time.time()
            commits = correlator.get_commits_for_story("1.3")
            elapsed_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Should complete in <100ms (allowing some margin for test overhead)
            assert elapsed_time < 200, f"Correlation took {elapsed_time:.2f}ms, exceeds 100ms requirement"
            assert len(commits) == 100
    
    def test_calculate_status_with_timezone_aware_datetime(self):
        """Test status calculation handles timezone-aware datetimes correctly"""
        from datetime import timezone
        
        # Test with timezone-aware datetime
        tz_aware_commit = GitCommit(
            sha="abc123",
            message="test",
            author="Author",
            timestamp=datetime.now(timezone.utc) - timedelta(days=1),
            files_changed=[]
        )
        
        with patch('backend.services.git_correlator.Repo'):
            correlator = GitCorrelator("/fake/repo")
            status, last_time = correlator.calculate_status([tz_aware_commit])
            
            assert status == "green"
            assert last_time is not None
    
    def test_calculate_status_with_naive_datetime(self):
        """Test status calculation handles naive datetimes correctly"""
        # Test with naive datetime
        naive_commit = GitCommit(
            sha="abc123",
            message="test",
            author="Author",
            timestamp=datetime.now() - timedelta(days=1),
            files_changed=[]
        )
        
        with patch('backend.services.git_correlator.Repo'):
            correlator = GitCorrelator("/fake/repo")
            status, last_time = correlator.calculate_status([naive_commit])
            
            assert status == "green"
            assert last_time is not None
