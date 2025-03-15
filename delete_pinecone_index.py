import os
from dotenv import load_dotenv
from pinecone import Pinecone

# Load environment variables
load_dotenv()

# Get Pinecone credentials from environment variables
api_key = os.environ.get('PINECONE_API_KEY')
index_name = os.environ.get('PINECONE_INDEX_NAME', 'sfold')

# Initialize Pinecone
pc = Pinecone(api_key=api_key)
print(f"Pinecone initialized successfully")

# Check if index exists
indexes = pc.list_indexes()
print(f"Available indexes: {indexes.names()}")

if index_name in indexes.names():
    print(f"Deleting index '{index_name}'")
    pc.delete_index(index_name)
    print(f"Index '{index_name}' deleted successfully")
else:
    print(f"Index '{index_name}' does not exist") 