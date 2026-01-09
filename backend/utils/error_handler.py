"""
BMAD Dash - Standardized Error Response Handler
"""
from flask import jsonify
from typing import Tuple


class ErrorHandler:
    """
    Provides standardized error responses
    Will be fully implemented in Story 1.1
    """
    
    @staticmethod
    def format_error(message: str, status_code: int = 500) -> Tuple[dict, int]:
        """
        Formats error response
        Will be implemented in Story 1.1
        """
        return jsonify({
            'error': True,
            'message': message,
            'status_code': status_code
        }), status_code
