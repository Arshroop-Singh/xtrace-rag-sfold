import os
from pinecone import Pinecone
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Pinecone credentials from environment variables
api_key = os.environ.get('PINECONE_API_KEY')
environment = os.environ.get('PINECONE_ENVIRONMENT')
index_name = os.environ.get('PINECONE_INDEX_NAME')

print(f"Testing Pinecone connection with:")
print(f"API Key: {api_key[:5]}...{api_key[-5:]}")
print(f"Environment: {environment}")
print(f"Index Name: {index_name}")

try:
    # Initialize Pinecone with the new API
    pc = Pinecone(api_key=api_key)
    print("Pinecone initialized successfully")
    
    # Check if index exists
    indexes = pc.list_indexes()
    print(f"Available indexes: {indexes.names()}")
    
    if index_name in indexes.names():
        print(f"Index '{index_name}' exists")
        
        # Connect to the index
        index = pc.Index(index_name)
        print(f"Connected to index '{index_name}'")
        
        # Get index stats
        stats = index.describe_index_stats()
        print(f"Index stats: {stats}")
        
        # Test a simple query with a random vector
        import numpy as np
        query_vector = np.random.rand(768).tolist()  # 768 dimensions for all-MiniLM-L6-v2
        
        results = index.query(
            vector=query_vector,
            top_k=5,
            include_metadata=True
        )
        
        print(f"Query results: {results}")
        print("Pinecone query successful")
        
    else:
        print(f"Index '{index_name}' does not exist")
        print("Would you like to create it? (y/n)")
        
except Exception as e:
    print(f"Error: {str(e)}") 