from functools import wraps
from flask import request, jsonify
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def api_key_required(f):
    """
    Decorator to check for API key authentication
    
    Args:
        f: The route function to wrap
    
    Returns:
        Wrapped function that checks for API key
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # For now, we're not implementing actual API key validation since
        # we're using the xtrace API key directly. This is just a placeholder
        # where you could add your own API key validation logic.
        
        # Log the request
        logger.info(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {request.method} {request.path}")
        
        return f(*args, **kwargs)
    return decorated_function

def request_logger(app):
    """
    Register request logging middleware for the Flask app
    
    Args:
        app: The Flask application
    """
    @app.before_request
    def log_request_info():
        logger.debug(f"Request Headers: {request.headers}")
        logger.debug(f"Request Body: {request.get_data()}")
        
    @app.after_request
    def log_response_info(response):
        logger.debug(f"Response Status: {response.status}")
        return response 