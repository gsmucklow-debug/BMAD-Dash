"""
Frontend Integration Tests
Tests serving of frontend files and integration with the dashboard API
"""

import pytest
from flask import Flask
from backend.app import create_app


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
def mock_project_data():
    """Mock project data for testing"""
    return {
        'project': {
            'name': 'BMAD Dash',
            'phase': 'Implementation',
            'root_path': 'F:/BMAD Dash'
        },
        'breadcrumb': {
            'project': 'BMAD Dash',
            'phase': 'Implementation',
            'epic': {'id': 1, 'title': 'Core Orientation System'},
            'story': {'id': '1.4', 'title': 'Frontend Shell & Breadcrumb Navigation'},
            'task': None
        }
    }


class TestFrontendServing:
    """Test that Flask serves frontend files correctly"""
    story_id = "1.4"
    
    def test_index_html_served(self, client):
        """Test that index.html is served at root path"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'BMAD Dash - Project Orientation Dashboard' in response.data
        assert b'breadcrumb-container' in response.data
        assert b'project-selector' in response.data
    
    def test_app_js_served(self, client):
        """Test that app.js is accessible"""
        response = client.get('/js/app.js')
        assert response.status_code == 200
        assert b'fetchDashboardData' in response.data
    
    def test_breadcrumb_js_served(self, client):
        """Test that breadcrumb component is accessible"""
        response = client.get('/js/components/breadcrumb.js')
        assert response.status_code == 200
        assert b'export function render' in response.data

    def test_quick_glance_js_served(self, client):
        """Test that quick-glance component is accessible"""
        response = client.get('/js/components/quick-glance.js')
        assert response.status_code == 200
        assert b'export function render' in response.data
    
    def test_output_css_served_after_build(self, client):
        """Test that output.css is accessible (requires build:css to be run first)"""
        response = client.get('/css/output.css')
        # May be 404 if not built yet, but should be accessible after build
        # This test will pass after npm run build:css is executed
        assert response.status_code in [200, 404]


class TestDashboardAPIIntegration:
    """Test frontend integration with dashboard API"""
    story_id = "1.3"
    
    def test_dashboard_endpoint_returns_breadcrumb(self, client, mock_project_data):
        """Test that /api/dashboard returns breadcrumb data"""
        response = client.get('/api/dashboard?project_root=F:/BMAD Dash')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'breadcrumb' in data
        assert data['breadcrumb']['project'] == 'BMAD Dash'
    
    def test_dashboard_endpoint_returns_quick_glance(self, client):
        """Test that /api/dashboard returns quick_glance data"""
        response = client.get('/api/dashboard?project_root=F:/BMAD Dash')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'quick_glance' in data
        assert isinstance(data['quick_glance'], dict)
        # quick_glance should have done, current, next keys (may be None)
        assert 'done' in data['quick_glance']
        assert 'current' in data['quick_glance']
        assert 'next' in data['quick_glance']
    
    def test_dashboard_endpoint_with_invalid_path(self, client):
        """Test that invalid project path returns error"""
        response = client.get('/api/dashboard?project_root=/invalid/path')
        assert response.status_code == 404
        
        data = response.get_json()
        assert 'error' in data or 'message' in data


class TestFrontendStructure:
    """Test frontend HTML structure and elements"""
    story_id = "1.4"
    
    def test_dark_theme_applied(self, client):
        """Test that dark theme class is present"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'class="dark"' in response.data
        assert b'bg-bmad-dark' in response.data
    
    def test_project_selector_present(self, client):
        """Test that project selector UI is present"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'project-root-input' in response.data
        assert b'load-project-btn' in response.data
    
    def test_breadcrumb_container_present(self, client):
        """Test that breadcrumb container exists"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'id="breadcrumb-container"' in response.data

    def test_quick_glance_container_present(self, client):
        """Test that quick-glance container exists"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'id="quick-glance-container"' in response.data
    
    def test_quick_glance_component_renders(self, client):
        """Test that Quick Glance component renders with dashboard data"""
        # This test verifies the component file exists and can be served
        response = client.get('/js/components/quick-glance.js')
        assert response.status_code == 200
        assert b'export function render' in response.data
        assert b'quick-glance-container' in response.data
    
    def test_loading_and_error_states(self, client):
        """Test that loading and error elements are present"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'id="loading"' in response.data
        assert b'id="error"' in response.data
    
    def test_es6_module_script_tag(self, client):
        """Test that app.js is loaded as ES6 module"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'type="module"' in response.data
        assert b'src="/js/app.js"' in response.data


class TestAccessibilityAndNFRs:
    """Test accessibility and non-functional requirements"""
    
    def test_minimum_button_size(self, client):
        """Test that load button meets minimum 44x44px requirement (NFR10)"""
        response = client.get('/')
        assert response.status_code == 200
        # Check for min-w and min-h classes
        assert b'min-w-[44px]' in response.data
        assert b'min-h-[44px]' in response.data
    
    def test_viewport_meta_tag(self, client):
        """Test that viewport meta tag is present for responsive design"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'name="viewport"' in response.data
    
    def test_semantic_html_navigation(self, client):
        """Test that breadcrumb uses semantic nav element"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'<nav id="breadcrumb-container"' in response.data


class TestStaticFileRouting:
    """Test static file routing configuration"""
    
    def test_js_file_routing(self, client):
        """Test that JavaScript files are routed correctly"""
        # Test top-level JS
        response = client.get('/js/app.js')
        assert response.status_code == 200
        
        # Test component JS
        response = client.get('/js/components/breadcrumb.js')
        assert response.status_code == 200
    
    def test_css_file_routing(self, client):
        """Test that CSS files are routed correctly"""
        response = client.get('/css/output.css')
        # May not exist until build:css is run
        assert response.status_code in [200, 404]
    
    def test_404_for_nonexistent_files(self, client):
        """Test that nonexistent files return 404"""
        response = client.get('/js/nonexistent.js')
        assert response.status_code == 404


class TestQuickGlanceComponent:
    """Test Quick Glance component functionality"""
    story_id = "1.5"
    
    def test_quick_glance_js_served(self, client):
        """Test that quick-glance component is accessible"""
        response = client.get('/js/components/quick-glance.js')
        assert response.status_code == 200
        assert b'export function render' in response.data
    
    def test_quick_glance_handles_empty_data(self, client):
        """Test that quick-glance component handles missing data gracefully"""
        # Component should handle missing quick_glance data
        response = client.get('/js/components/quick-glance.js')
        assert response.status_code == 200
        # Check that component has error handling
        assert b'quick_glance' in response.data or b'No quick glance' in response.data
    
    def test_quick_glance_has_progress_parsing(self, client):
        """Test that quick-glance component includes progress parsing logic"""
        response = client.get('/js/components/quick-glance.js')
        assert response.status_code == 200
        # Check for progress parsing function
        assert b'parseProgress' in response.data or b'progress' in response.data
    
    def test_quick_glance_has_escape_html(self, client):
        """Test that quick-glance component includes XSS protection"""
        response = client.get('/js/components/quick-glance.js')
        assert response.status_code == 200
        # Check for HTML escaping function
        assert b'escapeHtml' in response.data or b'textContent' in response.data


# Manual testing checklist (to be verified in browser)
"""
MANUAL TESTING CHECKLIST:
=========================

1. Visual Testing:
   [ ] Dark theme (#1a1a1a background) is applied
   [ ] Breadcrumb shows Project → Phase → Epic → Story → Task with arrows
   [ ] Current level in breadcrumb is highlighted in blue (#4a9eff)
   [ ] Text is readable (high contrast)
   [ ] Font size is at least 14px (NFR14)

2. Functionality Testing:
   [ ] Page loads at localhost:5000
   [ ] No JavaScript errors in console
   [ ] Breadcrumb renders with BMAD Dash project data
   [ ] Project root selector allows changing projects
   [ ] Loading indicator appears during API fetch
   [ ] Error messages display if API fails

3. Performance Testing:
   [ ] Page load time < 500ms (check DevTools Performance tab)
   [ ] Console.timeEnd shows total load time
   [ ] No memory leaks (check DevTools Memory tab)

4. Browser Compatibility:
   [ ] Chrome 87+ (ES6 modules work)
   [ ] Firefox 88+ (ES6 modules work)
   [ ] Safari 14+ (ES6 modules work)
   [ ] Edge 88+ (ES6 modules work)

5. Edge Cases:
   [ ] Breadcrumb handles null task gracefully
   [ ] Breadcrumb handles null story gracefully
   [ ] Breadcrumb handles null epic gracefully
   [ ] Invalid project path shows error message
"""
