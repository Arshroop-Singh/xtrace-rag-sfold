import os
from app.utils.vector import XTraceVectorDB

# Initialize the vector database client
def get_vector_db():
    """
    Get the XTraceVectorDB instance
    
    Returns:
        XTraceVectorDB instance
    """
    return XTraceVectorDB()  # No parameters needed

def query_vector_store(query_text, k=5):
    """
    Query the vector store for relevant chunks
    
    Args:
        query_text: The query text
        k: Number of chunks to retrieve
    
    Returns:
        List of relevant text chunks
    """
    if not query_text or not isinstance(query_text, str):
        raise ValueError("Query must be a non-empty string")
    
    vector_db = get_vector_db()
    return vector_db.query(query_text, k)