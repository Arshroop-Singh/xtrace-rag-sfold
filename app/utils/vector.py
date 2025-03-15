import os
import json
import requests
import PyPDF2
import time
import logging
from typing import Dict, List, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('xtrace_upload.log')
    ]
)
logger = logging.getLogger('xtrace')

class XTraceVectorDB:
    """
    A class to handle interactions with the XTrace Vector Database API
    """
    def __init__(self):
        """
        Initialize the XTrace Vector DB client with hardcoded values
        """
        logger.info("Initialized XTraceVectorDB with hardcoded credentials")
        logger.info("Using index_name=new-new-new and knowledge_base=test")
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
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
            return ""
    
    def chunk_text(self, text: str, chunk_size: Optional[int] = None, overlap: Optional[int] = None) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: The text to chunk
            chunk_size: The size of each chunk (defaults to self.chunk_size)
            overlap: The overlap between chunks (defaults to self.chunk_overlap)
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
        
        # Use instance defaults if not provided
        chunk_size = chunk_size or self.chunk_size
        overlap = overlap or self.chunk_overlap
            
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
    
    def upload_text(self, text: str, retry_count: int = 0) -> Dict:
        """
        Upload text to the vector database
        
        Args:
            text: The text to upload
            retry_count: Internal retry counter
            
        Returns:
            API response
        """
        if not text.strip():
            logger.warning("Empty text provided, skipping upload")
            return {"error": "Empty text provided"}
        
        url = "https://beta0-api.xtrace.ai/data"
        
        # Hardcoded payload with the same format as the working example
        payload = "{\n"
        payload += f"    \"context\": \"{text}\",\n"
        payload += "    \"index_name\": \"new-new-new\",\n"
        payload += "    \"knowledge_base\": \"test\"\n"
        payload += "}"
        
        # Hardcoded headers
        headers = {
            'x-api-key': 'pR4EPkE9AV5YlLVUlBqax5rN1jWMAPDbaO6Jysxp',
            'Content-Type': 'application/json'
        }
        
        logger.info(f"Uploading text chunk of length {len(text)}")
        
        try:
            # Copy the working example exactly
            response = requests.request("POST", url, headers=headers, data=payload)
            
            # Parse response
            response_json = response.json()
            
            # Check for success message in response
            if "response" in response_json and response_json["response"] == "data upload success!":
                return {"success": True}
            return response_json
            
        except Exception as e:
            logger.error(f"Error uploading text: {str(e)}")
            return {"error": str(e)}
    
    def upload_pdf(self, pdf_path: str) -> List[Dict]:
        """
        Process a PDF file and upload its content to the vector database
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of API responses for each chunk
        """
        filename = os.path.basename(pdf_path)
        logger.info(f"Starting upload process for {filename}")
        
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            logger.error(f"Failed to extract text from {filename}")
            return [{"error": f"Failed to extract text from {filename}"}]
        
        chunks = self.chunk_text(text)
        results = []
        
        logger.info(f"Uploading {len(chunks)} chunks from {filename}")
        
        for i, chunk in enumerate(chunks):
            logger.info(f"Uploading chunk {i+1}/{len(chunks)} from {filename}")
            result = self.upload_text(chunk)
            results.append(result)
            
            # Log success or failure
            if 'error' in result:
                logger.warning(f"Failed to upload chunk {i+1}/{len(chunks)} from {filename}: {result['error']}")
            else:
                logger.info(f"Successfully uploaded chunk {i+1}/{len(chunks)} from {filename}")
            
            # Always add a delay between uploads to avoid overwhelming the API
            # Use a longer delay after failures
            if 'error' in result:
                time.sleep(self.upload_delay * 2)
            else:
                time.sleep(self.upload_delay)
        
        # Summarize results
        success_count = sum(1 for r in results if 'success' in r)
        error_count = len(results) - success_count
        logger.info(f"Upload completed for {filename}: {success_count} chunks succeeded, {error_count} chunks failed")
        
        return results
    
    def upload_directory(self, directory_path: str, skip_on_error: bool = True) -> Dict[str, List[Dict]]:
        """
        Process all PDF files in a directory and upload their content
        
        Args:
            directory_path: Path to the directory containing PDF files
            skip_on_error: Whether to skip files that fail completely
            
        Returns:
            Dictionary mapping filenames to API responses
        """
        logger.info(f"Starting directory upload from {directory_path}")
        
        results = {}
        pdf_files = [f for f in os.listdir(directory_path) if f.lower().endswith('.pdf')]
        
        logger.info(f"Found {len(pdf_files)} PDF files in {directory_path}")
        
        for i, filename in enumerate(pdf_files):
            file_path = os.path.join(directory_path, filename)
            logger.info(f"Processing file {i+1}/{len(pdf_files)}: {filename}")
            
            try:
                file_results = self.upload_pdf(file_path)
                results[filename] = file_results
                
                # Add extra delay between files
                time.sleep(self.upload_delay * 2)
                
            except Exception as e:
                error_msg = f"Error processing {filename}: {str(e)}"
                logger.error(error_msg)
                
                if skip_on_error:
                    logger.info(f"Skipping file {filename} due to error")
                    results[filename] = [{"error": error_msg}]
                else:
                    raise
        
        return results
    
    def query(self, query_text: str, k: int = 5) -> List[str]:
        """
        Query the vector store for relevant chunks
        
        Args:
            query_text: The query text
            k: Number of chunks to retrieve
            
        Returns:
            List of relevant text chunks or a special error message if API is down
        """
        logger.info(f"Querying vector store with: '{query_text}', k={k}")
        
        url = "https://beta0-api.xtrace.ai/query"
        
        # Create payload EXACTLY like the working example
        payload = "{\n"
        payload += f"    \"query\": \"{query_text}\",\n"
        payload += f"    \"k\": \"1\",\n"
        payload += "    \"index_name\": \"new-new-new\",\n"
        payload += "    \"knowledge_base\": \"test\"\n"
        payload += "}"
        
        # Hardcoded headers exactly like the working example
        headers = {
            'x-api-key': 'pR4EPkE9AV5YlLVUlBqax5rN1jWMAPDbaO6Jysxp',
            'Content-Type': 'application/json'
        }
        
        try:
            # Copy the working example exactly
            response = requests.request("POST", url, headers=headers, data=payload)
            
            # Parse response
            response_json = response.json()
            chunks = response_json.get("response", [])
            
            logger.info(f"Retrieved {len(chunks)} chunks from vector store")
            return chunks
            
        except Exception as e:
            error_msg = f"API_ERROR: Vector database API is currently unavailable. Please try again later."
            logger.error(f"Error querying vector store: {str(e)}")
            return [error_msg]
    
    def ask_question(self, question: str, context_chunks: List[str] = None) -> str:
        """
        Ask a question to the vector database
        
        Args:
            question: The question to ask
            context_chunks: Optional pre-retrieved context chunks (for RAG)
            
        Returns:
            Answer to the question
        """
        logger.info(f"Asking question: '{question}'")
        
        # Get context chunks if not provided
        if context_chunks is None or len(context_chunks) == 0:
            logger.info("No context provided, retrieving context first")
            context_chunks = self.query(question, k=5)
            
            # Check if we got an API error
            if context_chunks and len(context_chunks) == 1 and context_chunks[0].startswith("API_ERROR:"):
                logger.error("Cannot ask question due to API error")
                return context_chunks[0]
            
            if not context_chunks or len(context_chunks) == 0:
                logger.warning("No context found for question, cannot provide accurate answer")
                return ""
        
        # Check for API error in provided context chunks
        if context_chunks and len(context_chunks) == 1 and context_chunks[0].startswith("API_ERROR:"):
            logger.error("Cannot ask question with provided context due to API error")
            return context_chunks[0]
        
        logger.info(f"Using {len(context_chunks)} context chunks to answer question")
        
        url = "https://beta0-api.xtrace.ai/question"
        
        # Join context chunks into a single context string
        context_text = " ".join(context_chunks)
        
        # Create payload with hardcoded values
        payload = "{\n"
        payload += f"    \"question\": \"{question}\",\n"
        payload += f"    \"context\": \"{context_text}\",\n"
        payload += "    \"index_name\": \"new-new-new\",\n"
        payload += "    \"knowledge_base\": \"test\"\n"
        payload += "}"
        
        # Hardcoded headers
        headers = {
            'x-api-key': 'pR4EPkE9AV5YlLVUlBqax5rN1jWMAPDbaO6Jysxp',
            'Content-Type': 'application/json'
        }
        
        try:
            # Copy the working example exactly
            response = requests.request("POST", url, headers=headers, data=payload)
            
            # Parse response
            response_json = response.json()
            answer = response_json.get("result", "")
            
            if answer:
                logger.info(f"Received answer of length {len(answer)}")
            else:
                logger.warning("Received empty answer")
                
            return answer
            
        except Exception as e:
            error_msg = f"API_ERROR: Vector database API is currently unavailable. Please try again later."
            logger.error(f"Error asking question: {str(e)}")
            return error_msg 