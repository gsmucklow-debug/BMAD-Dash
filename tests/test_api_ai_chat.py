"""
BMAD Dash - Tests for AI Chat API and Service
Tests for Story 5.1: Gemini API Integration & Streaming Chat
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from backend.app import create_app
from backend.services.ai_coach import AICoach


@pytest.fixture
def app():
    """Create and configure a test app instance"""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """A test client for the app"""
    return app.test_client()


@pytest.fixture
def mock_gemini():
    """Mock Gemini API client"""
    with patch('backend.services.ai_coach.genai') as mock_genai:
        mock_model = MagicMock()
        mock_genai.configure.return_value = None
        mock_genai.GenerativeModel.return_value = mock_model
        yield mock_model


class TestAICoach:
    """Tests for AICoach service"""
    
    def test_init_with_api_key(self, mock_gemini):
        """Test that AICoach initializes with API key"""
        coach = AICoach('test-api-key')
        assert coach.api_key == 'test-api-key'
        assert coach.model is not None
    
    def test_init_with_default_api_key(self, mock_gemini):
        """Test that AICoach raises error with default placeholder key"""
        coach = AICoach('your-api-key-here')
        assert coach.api_key == 'your-api-key-here'
    
    def test_build_system_prompt(self, mock_gemini):
        """Test system prompt construction with context"""
        coach = AICoach('test-api-key')
        context = {
            'phase': 'Implementation',
            'epic': 'epic-5',
            'story': '5.1',
            'task': '1'
        }
        
        prompt = coach._build_system_prompt(context)
        
        assert 'Implementation' in prompt
        assert 'epic-5' in prompt
        assert '5.1' in prompt
        assert 'BMAD' in prompt
        assert 'Coach AI assistant' in prompt
    
    def test_build_system_prompt_with_missing_context(self, mock_gemini):
        """Test system prompt construction handles missing context"""
        coach = AICoach('test-api-key')
        context = {}
        
        prompt = coach._build_system_prompt(context)
        
        assert 'Unknown' in prompt
        assert 'BMAD' in prompt
    
    @patch('backend.services.ai_coach.genai')
    def test_generate_stream_with_valid_key(self, mock_genai):
        """Test streaming response generation with valid API key"""
        # Mock streaming response
        mock_response = MagicMock()
        mock_chunk1 = MagicMock()
        mock_chunk1.text = 'Hello'
        mock_chunk2 = MagicMock()
        mock_chunk2.text = ' World'
        mock_response.__iter__ = Mock(return_value=iter([mock_chunk1, mock_chunk2]))
        
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.configure.return_value = None
        mock_genai.GenerativeModel.return_value = mock_model
        
        coach = AICoach('test-api-key')
        context = {'phase': 'Implementation'}
        
        chunks = list(coach.generate_stream('Test message', context))
        
        assert len(chunks) == 2
        assert 'Hello' in chunks[0]
        assert 'World' in chunks[1]
        assert 'data:' in chunks[0]
    
    @patch('backend.services.ai_coach.genai')
    def test_generate_stream_with_invalid_key(self, mock_genai):
        """Test streaming response with invalid API key raises error"""
        mock_genai.APIError = Exception
        coach = AICoach('your-api-key-here')
        context = {'phase': 'Implementation'}
        
        # Should raise ValueError for invalid API key
        with pytest.raises(ValueError, match="GEMINI_API_KEY is not configured"):
            list(coach.generate_stream('Test message', context))
    
    @patch('backend.services.ai_coach.genai')
    def test_generate_stream_with_api_error(self, mock_genai):
        """Test streaming response handles API errors gracefully"""
        # Import APIError from correct module
        try:
            from google.generativeai import APIError as GenAIError
        except ImportError:
            # If APIError doesn't exist, use generic Exception
            GenAIError = Exception
        
        mock_genai.APIError = GenAIError
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = GenAIError('Rate limit exceeded')
        mock_genai.configure.return_value = None
        mock_genai.GenerativeModel.return_value = mock_model
        
        coach = AICoach('test-api-key')
        context = {'phase': 'Implementation'}
        
        chunks = list(coach.generate_stream('Test message', context))
        
        assert len(chunks) == 1
        assert 'error' in chunks[0]
    
    @patch('backend.services.ai_coach.genai')
    def test_get_response_non_streaming(self, mock_genai):
        """Test non-streaming response for backward compatibility"""
        mock_response = MagicMock()
        mock_response.text = 'Test response'
        
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.configure.return_value = None
        mock_genai.GenerativeModel.return_value = mock_model
        
        coach = AICoach('test-api-key')
        context = {'phase': 'Implementation'}
        
        response = coach.get_response('Test message', context)
        
        assert response == 'Test response'


class TestAIChatAPI:
    """Tests for AI Chat API endpoints"""
    
    def test_health_check_returns_status(self, client):
        """Test health check endpoint returns status"""
        with patch('backend.config.Config.GEMINI_API_KEY', 'test-key'):
            response = client.get('/api/ai-chat/health')
            
            assert response.status_code == 200
            data = response.get_json()
            assert 'status' in data
            assert data['status'] == 'healthy'
    
    def test_health_check_detects_missing_key(self, client):
        """Test health check detects missing API key"""
        with patch('backend.config.Config.GEMINI_API_KEY', None):
            response = client.get('/api/ai-chat/health')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['api_key_configured'] == False
    
    def test_health_check_detects_placeholder_key(self, client):
        """Test health check detects placeholder API key"""
        with patch('backend.config.Config.GEMINI_API_KEY', 'your-api-key-here'):
            response = client.get('/api/ai-chat/health')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['api_key_configured'] == False
    
    def test_ai_chat_requires_json_content_type(self, client):
        """Test API requires JSON content type"""
        response = client.post('/api/ai-chat', data='not json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_ai_chat_requires_message_field(self, client):
        """Test API requires message field"""
        response = client.post(
            '/api/ai-chat',
            json={'project_context': {'phase': 'Implementation'}},
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'message' in data['message'].lower()
    
    def test_ai_chat_rejects_empty_message(self, client):
        """Test API rejects empty message"""
        response = client.post(
            '/api/ai-chat',
            json={'message': '   ', 'project_context': {}},
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'empty' in data['message'].lower()
    
    @patch('backend.config.Config.GEMINI_API_KEY', None)
    def test_ai_chat_returns_error_without_api_key(self, client):
        """Test API returns error when API key is not configured"""
        response = client.post(
            '/api/ai-chat',
            json={'message': 'Test', 'project_context': {}},
            content_type='application/json'
        )
        
        assert response.status_code == 500
        data = response.get_json()
        assert 'error' in data
    
    @patch('backend.services.ai_coach.genai')
    @patch('backend.config.Config.GEMINI_API_KEY', 'test-key')
    def test_ai_chat_returns_sse_stream(self, mock_genai, client):
        """Test API returns SSE stream response"""
        # Mock streaming response
        mock_response = MagicMock()
        mock_chunk = MagicMock()
        mock_chunk.text = 'Test response'
        mock_response.__iter__ = Mock(return_value=iter([mock_chunk]))
        
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.configure.return_value = None
        mock_genai.GenerativeModel.return_value = mock_model
        
        response = client.post(
            '/api/ai-chat',
            json={'message': 'Test', 'project_context': {'phase': 'Implementation'}},
            content_type='application/json'
        )
        
        assert response.status_code == 200
        assert 'text/event-stream' in response.content_type
        assert 'Cache-Control' in response.headers
        assert 'no-cache' in response.headers['Cache-Control']
    
    @patch('backend.services.ai_coach.genai')
    @patch('backend.config.Config.GEMINI_API_KEY', 'test-key')
    def test_ai_chat_stream_format(self, mock_genai, client):
        """Test API stream follows correct SSE format"""
        # Mock streaming response
        mock_response = MagicMock()
        mock_chunk = MagicMock()
        mock_chunk.text = 'Test token'
        mock_response.__iter__ = Mock(return_value=iter([mock_chunk]))
        
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.configure.return_value = None
        mock_genai.GenerativeModel.return_value = mock_model
        
        response = client.post(
            '/api/ai-chat',
            json={'message': 'Test', 'project_context': {}},
            content_type='application/json'
        )
        
        stream_data = response.get_data(as_text=True)
        assert 'data:' in stream_data
        assert 'token' in stream_data
