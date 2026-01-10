"""
BMAD Dash - Flask Application Entry Point
"""
from flask import Flask
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
    
    # Register other blueprints (will be added in later stories)
    # from backend.api import test_evidence, ai_chat, refresh
    
    @app.route('/')
    def index():
        return app.send_static_file('index.html')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
