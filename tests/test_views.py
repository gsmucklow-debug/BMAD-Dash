
import pytest
from backend.app import create_app

@pytest.fixture
def client():
    """Create a test client for the Flask application"""
    app = create_app()
    app.config['TESTING'] = True
    return app.test_client()

class TestViewStructure:
    """Test the structure of frontend views"""

    def test_dashboard_has_kanban_columns(self, client):
        """Verify dashboard view implements Kanban columns"""
        response = client.get('/js/views/dashboard.js')
        assert response.status_code == 200
        content = response.data.decode('utf-8')
        
        # Check for column titles
        assert 'To Do' in content
        assert 'In Progress' in content
        assert 'Review' in content
        assert 'Complete' in content
        
        # Check for render function
        assert 'renderKanbanBoard' in content

    def test_dashboard_has_action_card(self, client):
        """Verify dashboard view implements Action Card"""
        response = client.get('/js/views/dashboard.js')
        assert response.status_code == 200
        content = response.data.decode('utf-8')
        
        # Check for function import - Action Card is now a separate component
        assert 'renderActionCard' in content
        # Note: 'Current Focus' text is in quick-glance.js component, not dashboard.js

    def test_timeline_has_render_logic(self, client):
        """Verify timeline view implements event rendering"""
        response = client.get('/js/views/timeline.js')
        assert response.status_code == 200
        content = response.data.decode('utf-8')
        
        # Check for logic functions
        assert 'renderTimelineEvent' in content
        assert 'getTimelineEvents' in content
        
        # Check for event types
        assert 'completion' in content
        assert 'progress' in content
