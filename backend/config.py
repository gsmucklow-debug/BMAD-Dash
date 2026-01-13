"""
BMAD Dash - Configuration Management
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # BMAD Dash specific settings
    BMAD_ARTIFACTS_PATH = os.getenv('BMAD_ARTIFACTS_PATH', '_bmad-output')
    CACHE_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', '300'))  # 5 minutes default
    
    # AI Coach settings
    BMAD_DOCS_URL = os.getenv('BMAD_DOCS_URL', 'http://docs.bmad-method.org')
    BMAD_REPO_URL = os.getenv('BMAD_REPO_URL', 'https://github.com/bmad-code-org/BMAD-METHOD/archive/refs/heads/main.zip')
