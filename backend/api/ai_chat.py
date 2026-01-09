"""
BMAD Dash - AI Chat API Endpoint
POST /api/ai-chat - Sends message to AI coach and returns response
"""
from flask import Blueprint, request, jsonify

ai_chat_bp = Blueprint('ai_chat', __name__)


@ai_chat_bp.route('/api/ai-chat', methods=['POST'])
def ai_chat():
    """
    Processes AI chat messages
    Will be implemented in Story 3.1
    """
    return jsonify({
        'status': 'not_implemented',
        'message': 'AI chat endpoint will be implemented in Story 3.1'
    }), 501
