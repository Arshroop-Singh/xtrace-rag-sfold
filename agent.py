from nearai.agents.environment import Environment
import os
import sys
import logging

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.controllers.rag_controller import ask_question, get_context

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('agent')

def run(env: Environment):
    """
    Run the sFold expert agent
    
    Args:
        env: The NEAR AI agent environment
    """
    # System prompt defining the agent's role
    system_prompt = {
        "role": "system", 
        "content": "You are an expert with knowledge from all the sFold publications documents. Your job is to answer users by querying the vector database that consists of the latest publications on sFold. IMPORTANT: Only provide information if relevant content is found in the retrieved context. If no relevant information is found, politely state that you don't know. DO NOT use general knowledge to answer when no relevant context is found."
    }
    
    # Get user message
    user_message = env.list_messages()[-1] if env.list_messages() else None
    
    if user_message and user_message["role"] == "user" and user_message["content"]:
        query = user_message["content"]
        logger.info(f"Received user query: '{query}'")
        
        try:
            # Step 1: Retrieve relevant context chunks FIRST - this is the critical RAG step
            logger.info(f"Retrieving context for query")
            context_chunks = get_context(query, k=5)
            
            # Step 2: Check if we have any relevant context
            if not context_chunks or len(context_chunks) == 0:
                logger.warning("No relevant context found in vector store")
                # If no context is found, respond with "I don't know"
                no_info_message = {
                    "role": "system",
                    "content": "No relevant information was found in the sFold publications database for this query. Politely inform the user that you don't have information on this topic and can only answer questions related to sFold, RNA structures, microRNA research, and related topics covered in the sFold publications."
                }
                result = env.completion([system_prompt, no_info_message] + env.list_messages())
            else:
                # Step 3: Only when we have context, get a direct answer
                logger.info(f"Found {len(context_chunks)} relevant chunks, getting direct answer")
                direct_answer = ask_question(query)
                
                # Log chunks for debugging
                for i, chunk in enumerate(context_chunks):
                    logger.debug(f"Context chunk {i+1}: {chunk[:100]}...")
                
                # Step 4: Create context message with both the direct answer and supporting chunks
                context_message = {
                    "role": "system", 
                    "content": f"Here is relevant information from the sFold publications:\n\n{direct_answer}\n\nAdditional context:\n" + "\n\n".join(context_chunks)
                }
                
                # Generate a response using the NEAR AI model with context
                result = env.completion([system_prompt, context_message] + env.list_messages())
            
        except Exception as e:
            # If there's an error with the vector store, respond with error message
            logger.error(f"Error querying vector database: {str(e)}")
            error_message = {
                "role": "system",
                "content": "There was an error retrieving information from the database. Inform the user that you're unable to access the knowledge base at the moment."
            }
            result = env.completion([system_prompt, error_message] + env.list_messages())
    else:
        # If there's no user message, just use the system prompt
        result = env.completion([system_prompt] + env.list_messages())
    
    # Add the reply to the conversation
    env.add_reply(result)
    
    # Request further input from the user
    env.request_user_input()


run(env)