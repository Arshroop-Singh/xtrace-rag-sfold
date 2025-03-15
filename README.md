# sFold Expert RAG System

This project implements a Retrieval Augmented Generation (RAG) system using the XTrace vector database for processing PDF publications related to sFold research.

## Features

- PDF document processing and text extraction
- Chunking of text for efficient vector storage
- Integration with XTrace vector database
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
├── test_query.py       # Script to test vector database queries
├── upload_pdfs.py      # Script to upload PDFs to vector DB
├── .env                # Environment variables (create from .env.example)
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Setup

### Prerequisites

- Python 3.8+
- PDF documents to index

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
# XTrace API Configuration
XTRACE_API_KEY=pR4EPkE9AV5YlLVUlBqax5rN1jWMAPDbaO6Jysxp
XTRACE_INDEX_NAME=near-learning-club
XTRACE_KNOWLEDGE_BASE=publications

# Directory containing PDF files
PDF_DIRECTORY=sFold-Data

# Flask Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=False
```

> **Important Note:** The system is currently configured to use a specific API key and index name that are known to work with the XTrace API. If you need to use different values, you will need to modify the implementation accordingly.

## Usage

### Initial Setup: Uploading PDF Documents

Before the system can be used, PDF documents need to be uploaded to the vector database. This is a one-time administrative task performed using the `upload_pdfs.py` script.

To upload PDF documents to the vector database:

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

The upload process includes:
1. Extracting text from PDF documents
2. Splitting text into manageable chunks
3. Uploading chunks to the XTrace vector database
4. Handling retries and errors

#### Upload Options

The upload script supports various options to customize the upload process:

```
--file, -f            Single PDF file to upload
--directory, -d       Directory containing PDF files (default: sFold-Data)
--max-retries         Maximum number of retries for API calls (default: 5)
--retry-delay         Initial delay between retries in seconds (default: 10)
--chunk-size          Size of text chunks in characters (default: 600)
--chunk-overlap       Overlap between chunks in characters (default: 150)
--upload-delay        Delay between uploads in seconds (default: 2.0)
--skip-on-error       Skip files that fail completely
--verbose, -v         Enable verbose logging
```

### Testing the RAG System

To test the RAG system with a query:

```bash
# Test with a specific query
python main.py --query "What are the key findings of sFold research?"

# Specify number of context chunks to retrieve
python main.py --query "What are microRNA sponges?" --k 5

# Alternative test script
python test_query.py "What are microRNA sponges?" --k 3
```

### Running the API Server

To start the API server:

```bash
python main.py --api
```

The API will be available at `http://localhost:5000` with the following endpoints:

- `/api/rag/ask` - Ask a question to the RAG system
- `/api/rag/context` - Get relevant context for a query
- `/api/vector/query` - Query the vector store for relevant chunks
- `/health` - Health check endpoint

## Troubleshooting

### Server Errors During Upload

If you encounter 502 Server Error or other API errors during uploads:

1. Verify you're using the correct API key
2. Reduce the chunk size (e.g., `--chunk-size 400`)
3. Increase the upload delay to reduce load on the server (e.g., `--upload-delay 4.0`)
4. Check the upload logs for specific error messages (`upload_pdfs.log` and `xtrace_upload.log`)

### Connection Issues

If you're experiencing connection issues with the API:

1. Check your internet connection
2. Verify the API key and index name are correctly set
3. Try increasing the max retries (`--max-retries 10`)
4. Check if the XTrace API server is available

## Advanced Configuration

For advanced configuration options, see the `.env.example` file and the command-line arguments for each script. You can customize parameters such as:

- Chunk size and overlap for text processing
- Retry settings for API calls
- Logging verbosity
- Upload delay and batch processing options

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 