"""
Integration tests for Test Evidence API endpoint
"""
import pytest
from unittest.mock import patch, Mock
from datetime import datetime, timedelta
from backend.app import create_app
from backend.models.test_evidence import TestEvidence


@pytest.fixture
def client():
    """Create test client"""
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestTestEvidenceAPI:
    """Test suite for Test Evidence API endpoint"""
    
    def test_get_test_evidence_missing_project_root(self, client):
        """Test API returns 400 when project_root missing"""
        response = client.get('/api/test-evidence/2.3')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['error'] == 'MissingParameter'
        assert 'project_root' in data['message']
        assert data['status'] == 400
    
    def test_get_test_evidence_with_passing_tests(self, client):
        """Test API returns test evidence when tests found"""
        mock_evidence = TestEvidence(
            story_id="2.3",
            test_files=["tests/test_story_2_3.py"],
            pass_count=5,
            fail_count=0,
            failing_test_names=[],
            last_run_time=datetime.now(),
            status="green"
        )
        
        with patch('backend.api.test_evidence._check_story_exists', return_value=True):
            with patch('backend.api.test_evidence.TestDiscoverer') as MockDiscoverer:
                mock_discoverer = Mock()
                mock_discoverer.get_test_evidence_for_story.return_value = mock_evidence
                MockDiscoverer.return_value = mock_discoverer
                
                response = client.get('/api/test-evidence/2.3?project_root=/fake/repo')
                
                assert response.status_code == 200
                data = response.get_json()
                assert data['story_id'] == '2.3'
                assert data['pass_count'] == 5
                assert data['fail_count'] == 0
                assert data['total_tests'] == 5
                assert data['status'] == 'green'
                assert len(data['failing_test_names']) == 0
    
    def test_get_test_evidence_with_failing_tests(self, client):
        """Test API returns failing test details"""
        mock_evidence = TestEvidence(
            story_id="2.3",
            test_files=["tests/test_story_2_3.py"],
            pass_count=3,
            fail_count=2,
            failing_test_names=["test_feature_x", "test_feature_y"],
            last_run_time=datetime.now(),
            status="red"
        )
        
        with patch('backend.api.test_evidence._check_story_exists', return_value=True):
            with patch('backend.api.test_evidence.TestDiscoverer') as MockDiscoverer:
                mock_discoverer = Mock()
                mock_discoverer.get_test_evidence_for_story.return_value = mock_evidence
                MockDiscoverer.return_value = mock_discoverer
                
                response = client.get('/api/test-evidence/2.3?project_root=/fake/repo')
                
                assert response.status_code == 200
                data = response.get_json()
                assert data['story_id'] == '2.3'
                assert data['pass_count'] == 3
                assert data['fail_count'] == 2
                assert data['total_tests'] == 5
                assert data['status'] == 'red'
                assert len(data['failing_test_names']) == 2
                assert 'test_feature_x' in data['failing_test_names']
    
    def test_get_test_evidence_no_tests_found(self, client):
        """Test API returns unknown status when no tests found"""
        mock_evidence = TestEvidence(
            story_id="2.3",
            test_files=[],
            pass_count=0,
            fail_count=0,
            failing_test_names=[],
            last_run_time=None,
            status="unknown"
        )
        
        with patch('backend.api.test_evidence._check_story_exists', return_value=True):
            with patch('backend.api.test_evidence.TestDiscoverer') as MockDiscoverer:
                mock_discoverer = Mock()
                mock_discoverer.get_test_evidence_for_story.return_value = mock_evidence
                MockDiscoverer.return_value = mock_discoverer
                
                response = client.get('/api/test-evidence/2.3?project_root=/fake/repo')
                
                assert response.status_code == 200
                data = response.get_json()
                assert data['story_id'] == '2.3'
                assert data['status'] == 'unknown'
                assert data['total_tests'] == 0
                assert data['last_run_time'] is None
    
    def test_get_test_evidence_old_tests(self, client):
        """Test API returns yellow status for old tests"""
        old_time = datetime.now() - timedelta(days=2)
        mock_evidence = TestEvidence(
            story_id="2.3",
            test_files=["tests/test_story_2_3.py"],
            pass_count=5,
            fail_count=0,
            failing_test_names=[],
            last_run_time=old_time,
            status="yellow"
        )
        
        with patch('backend.api.test_evidence._check_story_exists', return_value=True):
            with patch('backend.api.test_evidence.TestDiscoverer') as MockDiscoverer:
                mock_discoverer = Mock()
                mock_discoverer.get_test_evidence_for_story.return_value = mock_evidence
                MockDiscoverer.return_value = mock_discoverer
                
                response = client.get('/api/test-evidence/2.3?project_root=/fake/repo')
                
                assert response.status_code == 200
                data = response.get_json()
                assert data['status'] == 'yellow'
                assert data['last_run_time'] is not None
    
    def test_get_test_evidence_error_handling(self, client):
        """Test API handles errors gracefully"""
        with patch('backend.api.test_evidence._check_story_exists', return_value=True):
            with patch('backend.api.test_evidence.TestDiscoverer') as MockDiscoverer:
                MockDiscoverer.side_effect = Exception("Test discovery error")
                
                response = client.get('/api/test-evidence/2.3?project_root=/fake/repo')
                
                assert response.status_code == 500
                data = response.get_json()
                assert data['error'] == 'TestDiscoveryError'
                assert 'Failed to retrieve' in data['message']
                assert data['status'] == 500
    
    def test_get_test_evidence_response_format(self, client):
        """Test API response matches expected format"""
        mock_evidence = TestEvidence(
            story_id="2.3",
            test_files=["tests/test_story_2_3.py"],
            pass_count=5,
            fail_count=0,
            failing_test_names=[],
            last_run_time=datetime.now(),
            status="green"
        )
        
        with patch('backend.api.test_evidence._check_story_exists', return_value=True):
            with patch('backend.api.test_evidence.TestDiscoverer') as MockDiscoverer:
                mock_discoverer = Mock()
                mock_discoverer.get_test_evidence_for_story.return_value = mock_evidence
                MockDiscoverer.return_value = mock_discoverer
                
                response = client.get('/api/test-evidence/2.3?project_root=/fake/repo')
                
                assert response.status_code == 200
                data = response.get_json()
                
                # Verify required fields
                assert 'story_id' in data
                assert 'test_files' in data
                assert 'pass_count' in data
                assert 'fail_count' in data
                assert 'total_tests' in data
                assert 'failing_test_names' in data
                assert 'last_run_time' in data
                assert 'status' in data
    
    def test_get_test_evidence_datetime_serialization(self, client):
        """Test API correctly serializes datetime objects"""
        test_time = datetime(2026, 1, 10, 12, 30, 45)
        mock_evidence = TestEvidence(
            story_id="2.3",
            test_files=["tests/test_story_2_3.py"],
            pass_count=5,
            fail_count=0,
            failing_test_names=[],
            last_run_time=test_time,
            status="green"
        )
        
        with patch('backend.api.test_evidence._check_story_exists', return_value=True):
            with patch('backend.api.test_evidence.TestDiscoverer') as MockDiscoverer:
                mock_discoverer = Mock()
                mock_discoverer.get_test_evidence_for_story.return_value = mock_evidence
                MockDiscoverer.return_value = mock_discoverer
                
                response = client.get('/api/test-evidence/2.3?project_root=/fake/repo')
                
                assert response.status_code == 200
                data = response.get_json()
                assert data['last_run_time'] == test_time.isoformat()
    
    def test_get_test_evidence_story_not_found(self, client):
        """Test API returns 404 when story file doesn't exist"""
        with patch('backend.api.test_evidence._check_story_exists') as mock_check:
            mock_check.return_value = False
            
            response = client.get('/api/test-evidence/99.99?project_root=/fake/repo')
            
            assert response.status_code == 404
            data = response.get_json()
            assert data['error'] == 'StoryNotFound'
            assert 'Story 99.99 not found' in data['message']
            assert data['status'] == 404
    
    def test_get_test_evidence_invalid_story_id(self, client):
        """Test API handles invalid story IDs gracefully - returns 404 if can't parse"""
        with patch('backend.api.test_evidence._check_story_exists') as mock_check:
            mock_check.return_value = False
            
            response = client.get('/api/test-evidence/invalid-story?project_root=/fake/repo')
            
            assert response.status_code == 404
            data = response.get_json()
            assert data['error'] == 'StoryNotFound'
    
    def test_get_test_evidence_performance_logging(self, client):
        """Test API logs performance metrics and meets <100ms requirement"""
        import time
        mock_evidence = TestEvidence(
            story_id="2.3",
            test_files=["tests/test_story_2_3.py"],
            pass_count=5,
            fail_count=0,
            failing_test_names=[],
            last_run_time=datetime.now(),
            status="green"
        )
        
        with patch('backend.api.test_evidence._check_story_exists', return_value=True):
            with patch('backend.api.test_evidence.TestDiscoverer') as MockDiscoverer:
                mock_discoverer = Mock()
                mock_discoverer.get_test_evidence_for_story.return_value = mock_evidence
                MockDiscoverer.return_value = mock_discoverer
                
                with patch('backend.api.test_evidence.logger') as mock_logger:
                    start_time = time.perf_counter()
                    response = client.get('/api/test-evidence/2.3?project_root=/fake/repo')
                    elapsed_time = (time.perf_counter() - start_time) * 1000  # Convert to ms
                    
                    assert response.status_code == 200
                    # Verify logging was called
                    assert mock_logger.info.called
                    # Verify performance requirement (NFR5: <100ms)
                    assert elapsed_time < 100, f"Response time {elapsed_time:.2f}ms exceeds 100ms requirement"
