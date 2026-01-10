"""
Integration tests for Git Evidence API endpoint
"""
import pytest
from unittest.mock import patch, Mock
from datetime import datetime, timedelta
from backend.app import create_app
from backend.models.git_evidence import GitCommit


@pytest.fixture
def client():
    """Create test client"""
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestGitEvidenceAPI:
    """Test suite for Git Evidence API endpoint"""
    
    def test_get_git_evidence_missing_project_root(self, client):
        """Test API returns 400 when project_root missing"""
        response = client.get('/api/git-evidence/1.3')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['error'] == 'MissingParameter'
        assert 'project_root' in data['message']
    
    def test_get_git_evidence_with_commits(self, client):
        """Test API returns commits when found"""
        mock_commit = GitCommit(
            sha="abc123",
            message="feat(story-1.3): Add feature",
            author="Test Author",
            timestamp=datetime.now(),
            files_changed=["backend/api/dashboard.py"]
        )
        
        with patch('backend.api.git_evidence.GitCorrelator') as MockCorrelator:
            mock_correlator = Mock()
            mock_correlator.get_commits_with_fallback.return_value = [mock_commit]
            mock_correlator.calculate_status.return_value = ("green", datetime.now())
            MockCorrelator.return_value = mock_correlator
            
            response = client.get('/api/git-evidence/1.3?project_root=/fake/repo')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['story_id'] == '1.3'
            assert len(data['commits']) == 1
            assert data['commits'][0]['sha'] == 'abc123'
            assert data['status'] == 'green'
    
    def test_get_git_evidence_no_commits(self, client):
        """Test API returns red status when no commits"""
        with patch('backend.api.git_evidence.GitCorrelator') as MockCorrelator:
            mock_correlator = Mock()
            mock_correlator.get_commits_with_fallback.return_value = []
            mock_correlator.calculate_status.return_value = ("red", None)
            MockCorrelator.return_value = mock_correlator
            
            response = client.get('/api/git-evidence/2.1?project_root=/fake/repo')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['story_id'] == '2.1'
            assert len(data['commits']) == 0
            assert data['status'] == 'red'
            assert data['last_commit_time'] is None
    
    def test_get_git_evidence_old_commits(self, client):
        """Test API returns yellow status for old commits"""
        old_commit = GitCommit(
            sha="def456",
            message="story-1.3: Old implementation",
            author="Old Author",
            timestamp=datetime.now() - timedelta(days=10),
            files_changed=[]
        )
        
        with patch('backend.api.git_evidence.GitCorrelator') as MockCorrelator:
            mock_correlator = Mock()
            mock_correlator.get_commits_with_fallback.return_value = [old_commit]
            old_time = datetime.now() - timedelta(days=10)
            mock_correlator.calculate_status.return_value = ("yellow", old_time)
            MockCorrelator.return_value = mock_correlator
            
            response = client.get('/api/git-evidence/1.3?project_root=/fake/repo')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'yellow'
            assert data['last_commit_time'] is not None
    
    def test_get_git_evidence_error_handling(self, client):
        """Test API handles errors gracefully"""
        with patch('backend.api.git_evidence.GitCorrelator') as MockCorrelator:
            MockCorrelator.side_effect = Exception("Git error")
            
            response = client.get('/api/git-evidence/1.3?project_root=/fake/repo')
            
            assert response.status_code == 500
            data = response.get_json()
            assert data['error'] == 'GitCorrelationError'
            assert 'Failed to retrieve' in data['message']
    
    def test_get_git_evidence_response_format(self, client):
        """Test API response matches expected format"""
        mock_commit = GitCommit(
            sha="abc123",
            message="test",
            author="Author",
            timestamp=datetime.now(),
            files_changed=["file.py"]
        )
        
        with patch('backend.api.git_evidence.GitCorrelator') as MockCorrelator:
            mock_correlator = Mock()
            mock_correlator.get_commits_with_fallback.return_value = [mock_commit]
            mock_correlator.calculate_status.return_value = ("green", datetime.now())
            MockCorrelator.return_value = mock_correlator
            
            response = client.get('/api/git-evidence/1.3?project_root=/fake/repo')
            
            assert response.status_code == 200
            data = response.get_json()
            
            # Verify required fields
            assert 'story_id' in data
            assert 'commits' in data
            assert 'status' in data
            assert 'last_commit_time' in data
            
            # Verify commit structure
            commit = data['commits'][0]
            assert 'sha' in commit
            assert 'message' in commit
            assert 'author' in commit
            assert 'timestamp' in commit
            assert 'files_changed' in commit
    
    def test_get_git_evidence_uses_fallback(self, client):
        """Test API uses fallback method when no Git commits found"""
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Test Story 2.1")
            temp_file = f.name
        
        try:
            with patch('backend.api.git_evidence.GitCorrelator') as MockCorrelator:
                mock_correlator = Mock()
                # Simulate no Git commits, fallback should be used
                mock_correlator.get_commits_with_fallback.return_value = []
                mock_correlator.calculate_status.return_value = ("red", None)
                MockCorrelator.return_value = mock_correlator
                
                response = client.get('/api/git-evidence/2.1?project_root=/fake/repo')
                
                # Verify get_commits_with_fallback was called (not get_commits_for_story)
                mock_correlator.get_commits_with_fallback.assert_called_once_with("2.1", "/fake/repo")
                
                assert response.status_code == 200
                data = response.get_json()
                assert data['status'] == 'red'
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
