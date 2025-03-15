import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Vector Database Configuration
PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY', '')
PINECONE_ENVIRONMENT = os.environ.get('PINECONE_ENVIRONMENT', 'gcp-starter')
PINECONE_INDEX_NAME = os.environ.get('PINECONE_INDEX_NAME', 'sfold')

# Directory containing PDF files
PDF_DIRECTORY = os.environ.get('PDF_DIRECTORY', 'sFold-Data')

# Flask Configuration
FLASK_HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.environ.get('FLASK_PORT', 5000))
FLASK_DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

# Check if required configuration is present
def validate_config():
    if not PINECONE_API_KEY:
        raise ValueError("PINECONE_API_KEY environment variable is not set")
    
    if not os.path.isdir(PDF_DIRECTORY):
        raise ValueError(f"PDF directory '{PDF_DIRECTORY}' does not exist") 