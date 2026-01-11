"""
BMAD Dash - Flask Application Entry Point
"""
from flask import Flask, request
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def create_app():
    """Application factory pattern"""
    app = Flask(__name__, 
                static_folder='../frontend',
                static_url_path='')
    
    # Configuration
    app.config['GEMINI_API_KEY'] = os.getenv('GEMINI_API_KEY')
    
    # JSON configuration
    app.config['JSON_AS_ASCII'] = False  # Allow Unicode in JSON responses
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True  # Pretty print in debug mode
    
    # Logging configuration
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Register blueprints
    from backend.api.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)
    
    # Register Git evidence blueprint (Story 2.1)
    from backend.api.git_evidence import git_evidence_bp
    app.register_blueprint(git_evidence_bp)
    
    # Register Test evidence blueprint (Story 2.3)
    from backend.api.test_evidence import test_evidence_bp
    app.register_blueprint(test_evidence_bp)
    
    # Register Review evidence blueprint (Story 3.2 Addendum)
    from backend.api.review_evidence import review_evidence_bp
    app.register_blueprint(review_evidence_bp)

    # Register Refresh blueprint (Story 3.3)
    from backend.api.refresh import refresh_bp
    app.register_blueprint(refresh_bp)

    # Register AI Chat blueprint (Story 5.1)
    from backend.api.ai_chat import ai_chat_bp
    app.register_blueprint(ai_chat_bp)
    
    @app.route('/')
    def index():
        return app.send_static_file('index.html')
    
    # Ensure CSS files are served with correct Content-Type
    @app.after_request
    def set_css_content_type(response):
        if response.content_type == 'application/octet-stream' and request.path.endswith('.css'):
            response.content_type = 'text/css'
        return response
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
