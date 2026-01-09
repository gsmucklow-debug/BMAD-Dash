"""
BMAD Dash - Standardized Error Response Handler
"""
from flask import jsonify
from typing import Tuple
from functools import wraps
import logging
import traceback

logger = logging.getLogger(__name__)


def handle_api_errors(f):
    """
    Decorator for API routes to provide standardized error handling
    
    Catches exceptions and returns consistent JSON error responses:
    - ValueError -> 400 Bad Request
    - FileNotFoundError -> 404 Not Found
    - Exception -> 500 Internal Server Error
    
    Error response format:
    {
        "error": "ExceptionType",
        "message": "User-friendly error message",
        "details": {...},
        "status": 400
    }
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            logger.warning(f"Bad Request (400): {str(e)}")
            return jsonify({
                "error": "ValueError",
                "message": str(e),
                "details": {},
                "status": 400
            }), 400
        except FileNotFoundError as e:
            logger.warning(f"Not Found (404): {str(e)}")
            return jsonify({
                "error": "FileNotFoundError",
                "message": str(e),
                "details": {},
                "status": 404
            }), 404
        except Exception as e:
            logger.error(f"Internal Server Error (500): {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({
                "error": type(e).__name__,
                "message": str(e),
                "details": {"traceback": traceback.format_exc()},
                "status": 500
            }), 500
    
    return decorated_function


class ErrorHandler:
    """
    Legacy error handler class - kept for backwards compatibility
    """
    
    @staticmethod
    def format_error(message: str, status_code: int = 500) -> Tuple[dict, int]:
        """
        Formats error response in standardized format
        """
        return jsonify({
            'error': 'Error',
            'message': message,
            'details': {},
            'status': status_code
        }), status_code
