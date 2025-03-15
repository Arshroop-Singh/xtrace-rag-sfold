import os
import sys
import logging
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('pinecone_query')

# Load environment variables
load_dotenv()

# Get Pinecone credentials from environment variables
api_key = os.environ.get('PINECONE_API_KEY')
index_name = os.environ.get('PINECONE_INDEX_NAME', 'sfold')

def query_pinecone(query_text, k=5):
    """
    Query the Pinecone vector database
    
    Args:
        query_text: The query text
        k: Number of results to return
        
    Returns:
        List of relevant text chunks
    """
    try:
        logger.info(f"Querying Pinecone with: '{query_text}', k={k}")
        
        # Initialize Pinecone
        pc = Pinecone(api_key=api_key)
        logger.info("Pinecone initialized successfully")
        
        # Connect to the index
        index = pc.Index(index_name)
        logger.info(f"Connected to index '{index_name}'")
        
        # Initialize the embedding model
        model = SentenceTransformer('all-MiniLM-L6-v2')  # This model produces 384-dimensional embeddings
        logger.info("Embedding model initialized")
        
        # Create embedding for the query
        query_embedding = model.encode(query_text).tolist()
        
        # Query Pinecone
        results = index.query(
            vector=query_embedding,
            top_k=k,
            include_metadata=True
        )
        
        # Extract text from metadata
        chunks = []
        for match in results['matches']:
            text = match['metadata'].get('text', '')
            source = match['metadata'].get('source', 'unknown')
            score = match['score']
            chunks.append({
                'text': text,
                'source': source,
                'score': score
            })
        
        logger.info(f"Retrieved {len(chunks)} chunks from Pinecone")
        return chunks
        
    except Exception as e:
        logger.error(f"Error querying Pinecone: {str(e)}")
        return []

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_pinecone_query.py 'your query here' [k]")
        return 1
    
    query = sys.argv[1]
    k = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    print(f"Querying Pinecone with: '{query}', k={k}")
    
    results = query_pinecone(query, k)
    
    if not results:
        print("No results found.")
        return 1
    
    print(f"\nFound {len(results)} relevant chunks:")
    for i, result in enumerate(results):
        print(f"\n--- Result {i+1} (Score: {result['score']:.4f}) from {result['source']} ---")
        print(result['text'])
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 