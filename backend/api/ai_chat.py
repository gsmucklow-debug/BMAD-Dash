"""
BMAD Dash - AI Chat API Endpoint
POST /api/ai-chat - Sends message to AI coach and returns streaming response
"""

from flask import Blueprint, request, Response, jsonify
from backend.services.ai_coach import AICoach
from backend.config import Config
import json

ai_chat_bp = Blueprint('ai_chat', __name__)


@ai_chat_bp.route('/api/ai-chat', methods=['POST'])
def ai_chat():
    """
    Processes AI chat messages and returns streaming response via SSE
    
    Request JSON:
    {
        "message": "User's question",
        "project_context": {
            "phase": "Implementation",
            "epic": "epic-5",
            "story": "5.1",
            "task": "1"
        }
    }
    
    Returns SSE stream with format: data: {"token": "..."}\n\n
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                'error': 'Invalid request',
                'message': 'Content-Type must be application/json'
            }), 400
        
        data = request.get_json()
        
        # Validate required fields
        if 'message' not in data:
            return jsonify({
                'error': 'Missing required field',
                'message': 'Field "message" is required'
            }), 400
        
        message = data.get('message', '').strip()
        project_context = data.get('project_context', {})
        
        if not message:
            return jsonify({
                'error': 'Invalid message',
                'message': 'Message cannot be empty'
            }), 400
        
        # Initialize AI Coach
        if not Config.GEMINI_API_KEY:
            return jsonify({
                'error': 'Configuration error',
                'message': 'GEMINI_API_KEY is not configured'
            }), 500
        
        # Get project root from context or use default
        project_root = project_context.get('project_root')
        if not project_root and hasattr(Config, 'PROJECT_ROOT'):
            project_root = Config.PROJECT_ROOT
        
        ai_coach = AICoach(Config.GEMINI_API_KEY, project_root=project_root)
        
        # Generate streaming response
        def generate():
            try:
                for chunk in ai_coach.generate_stream(message, project_context):
                    yield chunk
            except ValueError as e:
                error_data = {"error": str(e)}
                yield f"data: {json.dumps(error_data)}\n\n"
            except Exception as e:
                error_data = {"error": f"Internal server error: {str(e)}"}
                yield f"data: {json.dumps(error_data)}\n\n"
        
        return Response(
            generate(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no'  # Disable nginx buffering
            }
        )
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'details': 'An unexpected error occurred while processing the request'
        }), 500


@ai_chat_bp.route('/api/ai-chat/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for AI chat service
    
    Returns:
        JSON with status and API key configured flag
    """
    return jsonify({
        'status': 'healthy',
        'api_key_configured': bool(Config.GEMINI_API_KEY and Config.GEMINI_API_KEY != 'your-api-key-here')
    }), 200
