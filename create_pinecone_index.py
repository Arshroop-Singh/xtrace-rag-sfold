import os
import sys
import time
import logging
import argparse
import numpy as np
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
import PyPDF2
import traceback
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('pinecone_upload.log')
    ]
)
logger = logging.getLogger('pinecone_upload')

# Load environment variables
load_dotenv()

# Get Pinecone credentials from environment variables
api_key = os.environ.get('PINECONE_API_KEY')
environment = os.environ.get('PINECONE_ENVIRONMENT', 'gcp-starter')
index_name = os.environ.get('PINECONE_INDEX_NAME', 'sfold')
pdf_directory = os.environ.get('PDF_DIRECTORY', 'sFold-Data')

# Default constants for text processing (can be overridden by command line args)
DEFAULT_CHUNK_SIZE = 1200  # Increased from 600 to reduce number of chunks
DEFAULT_CHUNK_OVERLAP = 200
DEFAULT_BATCH_SIZE = 100  # Number of vectors to upload in a single batch
DEFAULT_UPLOAD_DELAY = 0.5  # Reduced delay between uploads
DEFAULT_MAX_PDFS = None  # Process all PDFs by default

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text from the PDF
    """
    try:
        logger.info(f"Extracting text from {pdf_path}")
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            total_pages = len(reader.pages)
            logger.info(f"PDF has {total_pages} pages")
            
            for page_num in range(total_pages):
                try:
                    page = reader.pages[page_num]
                    page_text = page.extract_text()
                    text += page_text + "\n\n"
                except Exception as e:
                    logger.warning(f"Error extracting text from page {page_num+1}: {str(e)}")
            
            logger.info(f"Extracted {len(text)} characters from {pdf_path}")
            return text
    except Exception as e:
        logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
        logger.error(traceback.format_exc())
        return ""

def chunk_text(text, chunk_size, overlap):
    """
    Split text into overlapping chunks
    
    Args:
        text: The text to chunk
        chunk_size: The size of each chunk
        overlap: The overlap between chunks
        
    Returns:
        List of text chunks
    """
    if not text:
        return []
        
    chunks = []
    start = 0
    text_length = len(text)
    
    logger.info(f"Chunking text of length {text_length} with chunk_size={chunk_size}, overlap={overlap}")
    
    while start < text_length:
        end = min(start + chunk_size, text_length)
        
        # Try to end at a sentence or paragraph boundary if possible
        if end < text_length:
            # Check for paragraph boundary
            paragraph_end = text.find('\n\n', end - 100, end + 100)
            if paragraph_end != -1 and paragraph_end < end + 100:
                end = paragraph_end + 2
            else:
                # Check for sentence boundary
                sentence_end = max(
                    text.find('. ', end - 50, end + 50),
                    text.find('? ', end - 50, end + 50),
                    text.find('! ', end - 50, end + 50)
                )
                if sentence_end != -1 and sentence_end < end + 50:
                    end = sentence_end + 2
        
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
    
    logger.info(f"Created {len(chunks)} chunks")
    return chunks

def batch_upload_chunks(index, chunks, pdf_file, model, batch_size, upload_delay):
    """
    Upload chunks to Pinecone in batches
    
    Args:
        index: Pinecone index
        chunks: List of text chunks
        pdf_file: Source PDF file name
        model: SentenceTransformer model
        batch_size: Number of vectors to upload in a single batch
        upload_delay: Delay between batch uploads in seconds
        
    Returns:
        Number of successfully uploaded chunks
    """
    total_chunks = len(chunks)
    success_count = 0
    batch_count = 0
    
    # Process chunks in batches
    for i in range(0, total_chunks, batch_size):
        batch = chunks[i:i+batch_size]
        batch_count += 1
        
        # Prepare vectors for batch upload
        vectors = []
        
        # Create embeddings for the batch
        logger.info(f"Creating embeddings for batch {batch_count} ({len(batch)} chunks)")
        
        # Process each chunk in the batch
        for j, chunk in enumerate(batch):
            chunk_index = i + j
            try:
                # Create a unique ID for this chunk
                chunk_id = f"{pdf_file.replace('.pdf', '').replace(' ', '_')}_{chunk_index}"
                
                # Create embedding
                embedding = model.encode(chunk).tolist()
                
                # Prepare metadata
                metadata = {
                    "source": pdf_file,
                    "chunk_index": chunk_index,
                    "total_chunks": total_chunks,
                    "text": chunk  # Store full text in metadata
                }
                
                # Add to vectors list for batch upload
                vectors.append((chunk_id, embedding, metadata))
                success_count += 1
                
            except Exception as e:
                logger.error(f"Error processing chunk {chunk_index+1}/{total_chunks} from {pdf_file}: {str(e)}")
        
        # Upload batch to Pinecone
        try:
            if vectors:
                logger.info(f"Uploading batch {batch_count} with {len(vectors)} vectors")
                index.upsert(vectors=vectors)
                logger.info(f"Successfully uploaded batch {batch_count}")
                
                # Add delay between batch uploads
                if upload_delay > 0:
                    time.sleep(upload_delay)
        except Exception as e:
            logger.error(f"Error uploading batch {batch_count}: {str(e)}")
            logger.error(traceback.format_exc())
    
    logger.info(f"Completed processing {pdf_file}: {success_count}/{total_chunks} chunks uploaded successfully")
    return success_count

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Create Pinecone index and upload PDF documents')
    parser.add_argument('--chunk-size', type=int, default=DEFAULT_CHUNK_SIZE,
                        help=f'Size of text chunks in characters (default: {DEFAULT_CHUNK_SIZE})')
    parser.add_argument('--chunk-overlap', type=int, default=DEFAULT_CHUNK_OVERLAP,
                        help=f'Overlap between chunks in characters (default: {DEFAULT_CHUNK_OVERLAP})')
    parser.add_argument('--batch-size', type=int, default=DEFAULT_BATCH_SIZE,
                        help=f'Number of vectors to upload in a single batch (default: {DEFAULT_BATCH_SIZE})')
    parser.add_argument('--upload-delay', type=float, default=DEFAULT_UPLOAD_DELAY,
                        help=f'Delay between batch uploads in seconds (default: {DEFAULT_UPLOAD_DELAY})')
    parser.add_argument('--max-pdfs', type=int, default=DEFAULT_MAX_PDFS,
                        help='Maximum number of PDFs to process (default: all)')
    parser.add_argument('--wait-time', type=int, default=30,
                        help='Wait time in seconds after creating index (default: 30)')
    parser.add_argument('--directory', type=str, default=pdf_directory,
                        help=f'Directory containing PDF files (default: {pdf_directory})')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose logging')
    return parser.parse_args()

def main():
    # Parse command line arguments
    args = parse_arguments()
    
    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Print configuration
    logger.info(f"Configuration:")
    logger.info(f"  Chunk size: {args.chunk_size}")
    logger.info(f"  Chunk overlap: {args.chunk_overlap}")
    logger.info(f"  Batch size: {args.batch_size}")
    logger.info(f"  Upload delay: {args.upload_delay}")
    logger.info(f"  Max PDFs: {args.max_pdfs if args.max_pdfs else 'all'}")
    logger.info(f"  PDF directory: {args.directory}")
    
    try:
        # Initialize Pinecone
        pc = Pinecone(api_key=api_key)
        logger.info("Pinecone initialized successfully")
        
        # Check if index exists
        indexes = pc.list_indexes()
        
        # Create index if it doesn't exist
        if index_name not in indexes.names():
            logger.info(f"Creating index '{index_name}'")
            pc.create_index(
                name=index_name,
                dimension=384,  # Dimension for all-MiniLM-L6-v2 is 384
                metric='cosine',
                spec=ServerlessSpec(cloud='aws', region='us-east-1')
            )
            logger.info(f"Index '{index_name}' created successfully")
            # Wait for index to be ready
            logger.info(f"Waiting {args.wait_time} seconds for index to be ready...")
            time.sleep(args.wait_time)
        else:
            logger.info(f"Index '{index_name}' already exists")
        
        # Connect to the index
        index = pc.Index(index_name)
        logger.info(f"Connected to index '{index_name}'")
        
        # Get initial stats
        initial_stats = index.describe_index_stats()
        logger.info(f"Initial index stats: {initial_stats}")
        
        # Initialize the embedding model
        model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Embedding model initialized")
        
        # Get list of PDF files
        pdf_files = [f for f in os.listdir(args.directory) if f.lower().endswith('.pdf')]
        
        # Limit the number of PDFs if specified
        if args.max_pdfs is not None and args.max_pdfs > 0:
            pdf_files = pdf_files[:args.max_pdfs]
            logger.info(f"Processing {len(pdf_files)} out of {len([f for f in os.listdir(args.directory) if f.lower().endswith('.pdf')])} PDF files")
        else:
            logger.info(f"Processing all {len(pdf_files)} PDF files")
        
        # Process each PDF file
        total_chunks_uploaded = 0
        for i, pdf_file in enumerate(pdf_files):
            logger.info(f"Processing file {i+1}/{len(pdf_files)}: {pdf_file}")
            pdf_path = os.path.join(args.directory, pdf_file)
            
            # Extract text from PDF
            text = extract_text_from_pdf(pdf_path)
            if not text:
                logger.error(f"Failed to extract text from {pdf_file}")
                continue
            
            # Chunk the text
            chunks = chunk_text(text, args.chunk_size, args.chunk_overlap)
            logger.info(f"Created {len(chunks)} chunks from {pdf_file}")
            
            # Upload chunks in batches
            chunks_uploaded = batch_upload_chunks(
                index=index,
                chunks=chunks,
                pdf_file=pdf_file,
                model=model,
                batch_size=args.batch_size,
                upload_delay=args.upload_delay
            )
            
            total_chunks_uploaded += chunks_uploaded
            
            # Log progress
            logger.info(f"Progress: {i+1}/{len(pdf_files)} files processed, {total_chunks_uploaded} total chunks uploaded")
            
            # Get intermediate stats every 5 files or for the last file
            if (i+1) % 5 == 0 or i == len(pdf_files) - 1:
                stats = index.describe_index_stats()
                logger.info(f"Intermediate index stats: {stats}")
        
        # Get final stats
        final_stats = index.describe_index_stats()
        logger.info(f"Final index stats: {final_stats}")
        
        logger.info(f"Upload process completed successfully. Total chunks uploaded: {total_chunks_uploaded}")
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        logger.error(traceback.format_exc())
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 