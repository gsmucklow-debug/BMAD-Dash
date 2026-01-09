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
    
    # Register blueprints (will be added in later stories)
    # from backend.api import dashboard, git_evidence, test_evidence, ai_chat, refresh
    
    @app.route('/')
    def index():
        return app.send_static_file('index.html')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
