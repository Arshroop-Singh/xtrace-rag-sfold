#!/usr/bin/env python3
import argparse
import os
import sys
from dotenv import load_dotenv

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def main():
    """
    Main entry point for the sFold Expert RAG Agent
    """
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='sFold Expert RAG Agent')
    parser.add_argument('--api', action='store_true', help='Start the API server')
    parser.add_argument('--query', '-q', help='Test a query against the vector database (e.g., "What are microRNA sponges?")')
    parser.add_argument('--k', type=int, default=3, help='Number of chunks to retrieve for a query')
    args = parser.parse_args()
    
    if args.api:
        # Start the API server
        print("Starting the API server...")
        from app.server import main as server_main
        return server_main()
    
    elif args.query:
        # Test a query
        print(f"Testing query: {args.query}")
        from app.controllers.rag_controller import ask_question, get_context
        
        # Get context chunks
        print("\nRetrieving context chunks...")
        context_chunks = get_context(args.query, k=args.k)
        
        print(f"\nRetrieved {len(context_chunks)} context chunks:")
        for i, chunk in enumerate(context_chunks):
            print(f"\n--- Chunk {i+1} ---")
            print(chunk[:500] + "..." if len(chunk) > 500 else chunk)
        
        # Get direct answer
        print("\nGetting direct answer...")
        answer = ask_question(args.query)
        
        print("\nDirect answer:")
        print(answer)
        
        return 0
    
    else:
        # Show help if no arguments provided
        parser.print_help()
        
        # Also suggest some example queries
        print("\nExample usage:")
        print("  Start API server:   python main.py --api")
        print("  Query examples:")
        print("    python main.py --query \"What are microRNA sponges?\"")
        print("    python main.py --query \"Explain the MicroRNA inhibition technique\" --k 5")
        print("    python main.py --query \"What technique is used for rapid generation of microRNA sponges?\"")
        return 0


if __name__ == "__main__":
    sys.exit(main()) 