from flask import Blueprint, request, jsonify
from app.controllers.vector_controller import query_vector_store

# Create blueprint for vector-related routes
vector_blueprint = Blueprint('vector', __name__)

@vector_blueprint.route('/query', methods=['POST'])
def query():
    """
    Endpoint to query the vector store for relevant chunks
    
    Request JSON:
    {
        "query": "Your query here",
        "k": 5  # optional, number of chunks to retrieve
    }
    
    Returns:
        JSON response with the chunks
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({"error": "Missing 'query' field in request"}), 400
        
        query_text = data['query']
        k = data.get('k', 5)
        
        if not isinstance(k, int) or k < 1:
            return jsonify({"error": "Parameter 'k' must be a positive integer"}), 400
        
        chunks = query_vector_store(query_text, k)
        
        return jsonify({"chunks": chunks}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500 