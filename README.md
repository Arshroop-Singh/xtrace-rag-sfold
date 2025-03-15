# sFold Expert RAG System

This project implements a Retrieval Augmented Generation (RAG) system using the Pinecone vector database for processing PDF publications related to sFold research.

## Features

- PDF document processing and text extraction
- Chunking of text for efficient vector storage
- Integration with Pinecone vector database
- REST API for querying the vector database
- NEAR AI agent implementation for answering user questions

## Project Structure

```
.
├── app/
│   ├── config/         # Configuration files
│   ├── controllers/    # Controller logic
│   ├── middleware/     # Middleware components
│   ├── routes/         # API routes
│   ├── utils/          # Utility functions
│   └── server.py       # Flask server
├── sFold-Data/         # Directory containing PDF files
├── agent.py            # NEAR AI agent implementation
├── main.py             # Main entry point script
├── create_pinecone_index.py  # Script to create Pinecone index and upload PDFs
├── delete_pinecone_index.py  # Script to delete Pinecone index
├── test_pinecone_query.py    # Script to test Pinecone queries
├── upload_pdfs.py      # Script to upload PDFs to vector DB
├── .env                # Environment variables (create from .env.example)
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Setup

### Prerequisites

- Python 3.8+
- PDF documents to index
- Pinecone account (free tier works fine)

### Installation

1. Clone this repository:
```
git clone <repository-url>
cd sfold-expert
```

2. Install the required dependencies:
```
pip install -r requirements.txt
```

3. Create a `.env` file based on the provided `.env.example`:
```
# Pinecone Vector Database Configuration
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=gcp-starter
PINECONE_INDEX_NAME=sfold

# Directory containing PDF files
PDF_DIRECTORY=sFold-Data

# Flask Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=False
```

## Pinecone Vector Database Management

### Creating and Populating the Pinecone Index

The `create_pinecone_index.py` script handles both creating the Pinecone index and uploading PDF documents to it. This is the recommended way to initialize your vector database.

```bash
# Create Pinecone index and upload all PDFs in the sFold-Data directory
python create_pinecone_index.py

# Process only the first 5 PDFs (useful for testing)
python create_pinecone_index.py --max-pdfs 5

# Use larger chunks to reduce the total number of chunks
python create_pinecone_index.py --chunk-size 2000 --chunk-overlap 300

# Speed up the upload process with larger batch size and no delay
python create_pinecone_index.py --batch-size 200 --upload-delay 0

# See all available options
python create_pinecone_index.py --help
```

#### Command-line Options

The script supports various options to customize the upload process:

```
--chunk-size        Size of text chunks in characters (default: 1200)
--chunk-overlap     Overlap between chunks in characters (default: 200)
--batch-size        Number of vectors to upload in a single batch (default: 100)
--upload-delay      Delay between batch uploads in seconds (default: 0.5)
--max-pdfs          Maximum number of PDFs to process (default: all)
--wait-time         Wait time in seconds after creating index (default: 30)
--directory         Directory containing PDF files (default: sFold-Data)
--verbose, -v       Enable verbose logging
```

The script will provide detailed logs of the upload process, including:
- Number of PDFs found
- Text extraction progress
- Chunking information
- Upload status for each batch
- Final statistics about the index

### Deleting the Pinecone Index

If you need to start fresh or remove the index completely, use the `delete_pinecone_index.py` script:

```bash
# Delete the Pinecone index
python delete_pinecone_index.py
```

This will completely remove the index and all its data. You'll need to recreate it using the `create_pinecone_index.py` script.

### Testing Pinecone Queries

To test if your Pinecone index is working correctly and contains the expected data:

```bash
# Test a query against the Pinecone index
python test_pinecone_query.py "What are microRNA sponges and how do they work?"

# Specify the number of results to return
python test_pinecone_query.py "What is RNA interference?" 10
```

This script will:
1. Connect to your Pinecone index
2. Convert your query to an embedding
3. Search for similar vectors in the index
4. Display the most relevant text chunks with their similarity scores

### Alternative: Using upload_pdfs.py

For more granular control over the upload process, you can use the `upload_pdfs.py` script:

```bash
# Upload a single PDF file
python upload_pdfs.py --file path/to/document.pdf

# Upload all PDFs in a directory
python upload_pdfs.py --directory path/to/pdf/directory

# Upload with custom chunk size and delay between uploads
python upload_pdfs.py --file path/to/document.pdf --chunk-size 400 --upload-delay 4.0

# More options
python upload_pdfs.py --help
```

#### Upload Options

The upload script supports various options to customize the upload process:

```
--file, -f            Single PDF file to upload
--directory, -d       Directory containing PDF files (default: sFold-Data)
--chunk-size          Size of text chunks in characters (default: 600)
--chunk-overlap       Overlap between chunks in characters (default: 150)
--upload-delay        Delay between uploads in seconds (default: 2.0)
--skip-on-error       Skip files that fail completely
--verbose, -v         Enable verbose logging
```

## Running the System

### Testing the RAG System

To test the RAG system with a query:

```bash
# Test with a specific query
python main.py --query "What are the key findings of sFold research?"

# Specify number of context chunks to retrieve
python main.py --query "What are microRNA sponges?" --k 5
```

### Running the API Server

To start the API server:

```bash
# Start the API server
python main.py --api
```

The server will be available at `http://localhost:5000` (or the port specified in your .env file).

#### Web Interface

A simple web interface is available at the root URL (`http://localhost:5000/`). This provides a chat-like interface to interact with the sFold Expert system.

#### API Endpoints

The following API endpoints are available:

- `POST /api/rag/ask` - Ask a question to the RAG system
  ```json
  {
    "question": "What are microRNA sponges?"
  }
  ```

- `POST /api/rag/context` - Get relevant context for a query
  ```json
  {
    "query": "What are microRNA sponges?",
    "k": 5
  }
  ```

- `POST /api/vector/query` - Query the vector store for relevant chunks
  ```json
  {
    "query": "What are microRNA sponges?",
    "k": 5
  }
  ```

- `GET /health` - Health check endpoint

### Environment Management

It's recommended to use a dedicated Python environment for this project:

```bash
# Create a new conda environment
conda create -n sfold-env python=3.9

# Activate the environment
conda activate sfold-env

# Install dependencies
pip install -r requirements.txt
```

## Troubleshooting

### Common Issues and Solutions

#### Empty Results from Queries

If your queries return no results:

1. Check if the Pinecone index has data:
   ```python
   from pinecone import Pinecone
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   pc = Pinecone(api_key=os.environ.get('PINECONE_API_KEY'))
   index = pc.Index(os.environ.get('PINECONE_INDEX_NAME', 'sfold'))
   print(index.describe_index_stats())
   ```

2. Adjust the relevance threshold in `app/utils/vector.py`:
   - Default is 0.2 (lower values return more results but may be less relevant)
   - Try values between 0.1 and 0.3 depending on your needs

#### Server Errors During Upload

If you encounter 502 Server Error or other API errors during uploads:

1. Verify you're using the correct API key
2. Reduce the chunk size (e.g., `--chunk-size 400`)
3. Increase the upload delay to reduce load on the server (e.g., `--upload-delay 4.0`)
4. Check the upload logs for specific error messages (`pinecone_upload.log`)

#### Server Already Running

If you get "Address already in use" errors:

```bash
# Find and kill the running Flask server
pkill -f "python main.py --api"

# Then start the server again
python main.py --api
```

#### Pinecone Module Not Found

If you get "ModuleNotFoundError: No module named 'pinecone'":

```bash
# Install the Pinecone client
pip install pinecone-client==2.2.4 sentence-transformers==2.2.2
```

## Advanced Configuration

### Adjusting Relevance Threshold

The relevance threshold determines how similar a document must be to your query to be included in results:

1. Open `app/utils/vector.py`
2. Find the `__init__` method of the `PineconeVectorDB` class
3. Adjust the `relevance_threshold` parameter (default is 0.2)
   - Lower values (e.g., 0.1) return more results but may include less relevant content
   - Higher values (e.g., 0.4) return fewer, more relevant results

### Customizing Chunking Parameters

Text chunking parameters can be adjusted to optimize for your specific documents:

1. Open `app/utils/vector.py` or use command-line parameters
2. Adjust the following parameters:
   - `chunk_size`: Size of text chunks in characters (default: 600)
   - `chunk_overlap`: Overlap between chunks in characters (default: 150)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 