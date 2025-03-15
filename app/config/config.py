import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# XTrace API Configuration
XTRACE_API_KEY = os.environ.get('XTRACE_API_KEY', '')
XTRACE_INDEX_NAME = os.environ.get('XTRACE_INDEX_NAME', 'sfold')
XTRACE_KNOWLEDGE_BASE = os.environ.get('XTRACE_KNOWLEDGE_BASE', 'publications')

# Directory containing PDF files
PDF_DIRECTORY = os.environ.get('PDF_DIRECTORY', 'sFold-Data')

# Flask Configuration
FLASK_HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.environ.get('FLASK_PORT', 5000))
FLASK_DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

# Check if required configuration is present
def validate_config():
    if not XTRACE_API_KEY:
        raise ValueError("XTRACE_API_KEY environment variable is not set")
    
    if not os.path.isdir(PDF_DIRECTORY):
        raise ValueError(f"PDF directory '{PDF_DIRECTORY}' does not exist") 