
import pytest
from backend.app import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_dashboard_returns_cache_age(client):
    """Test that dashboard response includes cache age"""
    response = client.get('/api/dashboard?project_root=.')
    assert response.status_code == 200
    data = response.get_json()
    assert 'cache_age_ms' in data
