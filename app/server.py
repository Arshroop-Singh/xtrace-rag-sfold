from flask import Flask, request, jsonify, render_template
import os
import sys

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG, validate_config
from app.routes.rag_routes import rag_blueprint
from app.routes.vector_routes import vector_blueprint
from app.middleware.auth import request_logger

def create_app():
    """
    Create and configure the Flask application
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates')
    
    # Register middleware
    request_logger(app)
    
    # Register blueprints
    app.register_blueprint(rag_blueprint, url_prefix='/api/rag')
    app.register_blueprint(vector_blueprint, url_prefix='/api/vector')
    
    # Home route for the chat interface
    @app.route('/', methods=['GET'])
    def home():
        return render_template('chat.html')
    
    # Create a simple health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy"}), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found"}), 404
    
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({"error": "Internal server error"}), 500
    
    return app

def main():
    """
    Main entry point for the Flask application
    """
    try:
        # Validate configuration
        validate_config()
        
        # Create and run the app
        app = create_app()
        app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
        
    except Exception as e:
        print(f"Error starting server: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 