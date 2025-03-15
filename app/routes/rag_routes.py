from flask import Blueprint, request, jsonify
from app.controllers.rag_controller import ask_question, get_context

# Create blueprint for RAG-related routes
rag_blueprint = Blueprint('rag', __name__)

@rag_blueprint.route('/ask', methods=['POST'])
def ask():
    """
    Endpoint to ask a question to the RAG system
    
    Request JSON:
    {
        "question": "Your question here"
    }
    
    Returns:
        JSON response with the answer
    """
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({"error": "Missing 'question' field in request"}), 400
        
        question = data['question']
        answer = ask_question(question)
        
        return jsonify({"answer": answer}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@rag_blueprint.route('/context', methods=['POST'])
def context():
    """
    Endpoint to get relevant context for a query
    
    Request JSON:
    {
        "query": "Your query here",
        "k": 5  # optional, number of chunks to retrieve
    }
    
    Returns:
        JSON response with the context chunks
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({"error": "Missing 'query' field in request"}), 400
        
        query = data['query']
        k = data.get('k', 5)
        
        if not isinstance(k, int) or k < 1:
            return jsonify({"error": "Parameter 'k' must be a positive integer"}), 400
        
        context = get_context(query, k)
        
        return jsonify({"context": context}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500 