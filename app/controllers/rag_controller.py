from app.controllers.vector_controller import get_vector_db
import logging

# Configure logging
logger = logging.getLogger('rag_controller')

def ask_question(question):
    """
    Ask a question to the RAG system using proper RAG flow
    
    Args:
        question: The question to ask
    
    Returns:
        Answer to the question based on retrieved context, or "I don't know" message
    """
    if not question or not isinstance(question, str):
        raise ValueError("Question must be a non-empty string")
    
    # Step 1: Initialize the vector database client
    vector_db = get_vector_db()
    
    # Step 2: Get relevant context chunks FIRST
    logger.info(f"Retrieving context for question: '{question}'")
    context_chunks = vector_db.query(question, k=5)
    
    # Check if API returned an error
    if context_chunks and len(context_chunks) == 1 and context_chunks[0].startswith("API_ERROR:"):
        logger.error(f"API error occurred: {context_chunks[0]}")
        return f"I'm sorry, I'm currently unable to access my knowledge base. The server returned the following error: {context_chunks[0].replace('API_ERROR: ', '')}"
    
    # Step 3: Check if we have any relevant context
    if not context_chunks or len(context_chunks) == 0:
        logger.warning(f"No relevant context found for question: '{question}'")
        return "I don't have information about this topic in my knowledge base. I can only answer questions related to sFold, RNA structures, microRNA research, and topics covered in the sFold publications."
    
    # Step 4: Log the retrieved chunks for debugging
    logger.info(f"Found {len(context_chunks)} relevant chunks for question: '{question}'")
    for i, chunk in enumerate(context_chunks):
        logger.debug(f"Context chunk {i+1}: {chunk[:100]}...")
    
    # Step 5: Only when we have context, ask the question WITH the context
    answer = vector_db.ask_question(question, context_chunks=context_chunks)
    
    # Check if API returned an error
    if answer and answer.startswith("API_ERROR:"):
        logger.error(f"API error occurred: {answer}")
        return f"I'm sorry, I'm currently unable to generate an answer. The server returned the following error: {answer.replace('API_ERROR: ', '')}"
    
    # Step 6: Final check on the answer
    if not answer or len(answer.strip()) < 20 or "I don't have" in answer or "I don't know" in answer:
        logger.warning(f"Received empty or generic answer from vector DB: '{answer}'")
        return "I don't have information about this topic in my knowledge base. I can only answer questions related to sFold, RNA structures, microRNA research, and topics covered in the sFold publications."
    
    # Return the context-based answer
    return answer

def get_context(query, k=5):
    """
    Get relevant context for a query
    
    Args:
        query: The query text
        k: Number of chunks to retrieve
    
    Returns:
        List of relevant text chunks
    """
    if not query or not isinstance(query, str):
        raise ValueError("Query must be a non-empty string")
    
    vector_db = get_vector_db()
    context = vector_db.query(query, k)
    
    # Check if API returned an error
    if context and len(context) == 1 and context[0].startswith("API_ERROR:"):
        logger.error(f"API error occurred: {context[0]}")
        # Return the API error message
        return context
    
    # Log when no context is found
    if not context or len(context) == 0:
        logger.warning(f"No context found for query: '{query}'")
    
    return context