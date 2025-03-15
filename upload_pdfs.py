import os
import sys
import json
import argparse
import time
import logging
from dotenv import load_dotenv

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.vector import PineconeVectorDB
from app.config.config import PINECONE_API_KEY, PINECONE_ENVIRONMENT, PINECONE_INDEX_NAME

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('upload_pdfs.log')
    ]
)
logger = logging.getLogger('upload_script')

def main():
    """
    Main entry point for the PDF upload script
    """
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Upload PDF files to the Pinecone vector database')
    parser.add_argument('--directory', '-d', help='Directory containing PDF files', default='sFold-Data')
    parser.add_argument('--file', '-f', help='Single PDF file to upload')
    parser.add_argument('--chunk-size', type=int, default=600, help='Size of text chunks in characters')
    parser.add_argument('--chunk-overlap', type=int, default=150, help='Overlap between chunks in characters')
    parser.add_argument('--upload-delay', type=float, default=2.0, help='Delay between uploads in seconds')
    parser.add_argument('--skip-on-error', action='store_true', help='Skip files that fail completely')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    args = parser.parse_args()
    
    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger('pinecone').setLevel(logging.DEBUG)
    
    start_time = time.time()
    
    try:
        logger.info(f"Starting upload at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Using chunking settings: chunk_size={args.chunk_size}, chunk_overlap={args.chunk_overlap}")
        logger.info(f"Using upload_delay={args.upload_delay}s between uploads")
        
        # Initialize vector database client with command line parameters
        vector_db = PineconeVectorDB(
            api_key=PINECONE_API_KEY,
            environment=PINECONE_ENVIRONMENT,
            index_name=PINECONE_INDEX_NAME,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            upload_delay=args.upload_delay
        )
        
        if args.file:
            # Upload a single file
            logger.info(f"Uploading file: {args.file}")
            results = vector_db.upload_pdf(args.file)
            
            # Count successful and failed chunks
            success_count = sum(1 for chunk_result in results if 'success' in chunk_result)
            error_count = len(results) - success_count
            
            logger.info(f"Upload complete for file: {args.file}")
            logger.info(f"Successfully uploaded {success_count} chunks")
            logger.info(f"Failed to upload {error_count} chunks")
            
        else:
            # Upload all PDF files in the directory
            logger.info(f"Uploading all PDF files in directory: {args.directory}")
            
            # Get list of PDF files
            pdf_files = [f for f in os.listdir(args.directory) if f.lower().endswith('.pdf')]
            total_files = len(pdf_files)
            
            logger.info(f"Found {total_files} PDF files to process")
            
            # Process each file
            results = vector_db.upload_directory(args.directory, skip_on_error=args.skip_on_error)
            
            # Count successful and failed chunks
            success_count = 0
            error_count = 0
            processed_files = len(results)
            
            for file_name, file_results in results.items():
                file_success = sum(1 for chunk_result in file_results if 'success' in chunk_result)
                file_error = len(file_results) - file_success
                
                success_count += file_success
                error_count += file_error
                
                logger.info(f"File {file_name}: {file_success} chunks succeeded, {file_error} chunks failed")
            
            logger.info(f"Upload complete. Processed {processed_files}/{total_files} files.")
            logger.info(f"Successfully uploaded {success_count} chunks")
            logger.info(f"Failed to upload {error_count} chunks")
        
        elapsed_time = time.time() - start_time
        logger.info(f"Total time elapsed: {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)")
    
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 