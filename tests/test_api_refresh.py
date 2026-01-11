"""
BMAD Dash - Refresh API Endpoint Tests
Tests for Story 3.3: Minimal List View & Manual Refresh
"""
import pytest
import os
import time
from backend.app import create_app
from backend.api.dashboard import _cache


@pytest.fixture
def app():
    """Create and configure a test Flask application"""
    app = create_app()
    app.config['TESTING'] = True
    yield app


@pytest.fixture
def client(app):
    """Create a test client for the Flask application"""
    return app.test_client()


@pytest.fixture
def bmad_dash_project_root():
    """Returns the actual BMAD Dash project root path"""
    # Tests run from within the BMAD Dash project
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture
def clear_cache():
    """Clear the global cache before each test"""
    _cache.invalidate_all()
    yield
    _cache.invalidate_all()


class TestRefreshEndpoint:
    """Test suite for /api/refresh endpoint"""

    def test_refresh_success(self, client, bmad_dash_project_root, clear_cache):
        """
        Test successful cache refresh with valid project_root

        Acceptance Criteria:
        - POST /api/refresh?project_root=<path> returns 200
        - Response contains status='cache_cleared'
        - Response contains timestamp
        """
        # Call refresh endpoint
        response = client.post(f'/api/refresh?project_root={bmad_dash_project_root}')

        # Verify response
        assert response.status_code == 200
        data = response.get_json()

        assert data['status'] == 'cache_cleared'
        assert 'timestamp' in data
        assert 'project_root' in data
        assert data['project_root'] == bmad_dash_project_root
        
        # New field added
        assert 'deleted_file' in data

    def test_refresh_missing_project_root(self, client, clear_cache):
        """
        Test refresh endpoint without project_root parameter

        Acceptance Criteria:
        - Returns 400 Bad Request
        - Response contains error message
        """
        response = client.post('/api/refresh')

        assert response.status_code == 400
        data = response.get_json()

        assert data['error'] == 'MissingParameter'
        assert 'project_root' in data['message'].lower()


    def test_refresh_preserves_project_root(self, client, bmad_dash_project_root, clear_cache):
        """
        Test that refresh returns the correct project_root

        Acceptance Criteria:
        - Response contains the project_root from request
        """
        response = client.post(f'/api/refresh?project_root={bmad_dash_project_root}')

        assert response.status_code == 200
        data = response.get_json()
        assert data['project_root'] == bmad_dash_project_root

    def test_refresh_performance_nfr7(self, client, bmad_dash_project_root, clear_cache):
        """
        Test that refresh completes in <300ms (NFR7)

        Acceptance Criteria:
        - Refresh endpoint completes in <300ms
        - Performance is measured from request start to response
        """
        # Warm up
        client.post(f'/api/refresh?project_root={bmad_dash_project_root}')

        # Measure actual performance
        times = []
        for _ in range(5):  # Run 5 times and take average
            start = time.time()
            response = client.post(f'/api/refresh?project_root={bmad_dash_project_root}')
            duration = (time.time() - start) * 1000
            times.append(duration)
            assert response.status_code == 200

        avg_time = sum(times) / len(times)
        max_time = max(times)

        # All runs should be under 300ms
        assert max_time < 300, f"Max refresh time {max_time:.2f}ms exceeded 300ms (NFR7)"
        print(f"Average refresh time: {avg_time:.2f}ms, Max: {max_time:.2f}ms")
