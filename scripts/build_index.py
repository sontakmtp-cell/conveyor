# Copilot: Implement strictly per comments.
# Do NOT reference or display the original PDF name or path anywhere in UI or logs.
# Citations must be anonymous: {"page": int, "section": str|None}.
# Build-time uses PDF, runtime uses only the persisted index.

import os
import sys
from dotenv import load_dotenv
from pathlib import Path

# Add parent directory to path so we can import core
sys.path.append(str(Path(__file__).parent.parent))

from core.rag.pdf_loader import load_pdf_chunks
from core.rag.index import build_index

def main():
    # Get the root directory of the project
    root_dir = Path(__file__).parent.parent.absolute()
    
    # Load environment variables from .env file in root directory
    dotenv_path = root_dir / '.env'
    if not dotenv_path.exists():
        print(f"Error: .env file not found at {dotenv_path}")
        sys.exit(1)
    
    load_dotenv(dotenv_path=dotenv_path)
    
    pdf_path = os.getenv('PDF_PATH')
    index_dir = os.getenv('INDEX_DIR')
    
    if not pdf_path or not index_dir:
        print("Error: PDF_PATH and INDEX_DIR must be set in .env file")
        print(f"Current values:")
        print(f"PDF_PATH = {pdf_path}")
        print(f"INDEX_DIR = {index_dir}")
        sys.exit(1)
        
    # Convert relative paths to absolute if needed
    if not os.path.isabs(pdf_path):
        pdf_path = os.path.join(root_dir, pdf_path)
    if not os.path.isabs(index_dir):
        index_dir = os.path.join(root_dir, index_dir)
    
    # Create chunks from PDF
    print("Loading PDF chunks...")
    chunks = load_pdf_chunks(pdf_path)
    
    # Print statistics
    total_chunks = len(chunks)
    total_tokens = sum(len(chunk.text.split()) for chunk in chunks)
    avg_chunk_size = total_tokens / total_chunks if total_chunks > 0 else 0
    
    print(f"\nStatistics:")
    print(f"Number of chunks: {total_chunks}")
    print(f"Average chunk size (words): {avg_chunk_size:.1f}")
    
    # Build search index
    print("\nBuilding search index...")
    build_index(chunks, index_dir)
    
    print(f"\nIndex built successfully and saved to {index_dir}")
    print("\nYou can now delete or move the source PDF - only the index is needed for runtime.")

if __name__ == "__main__":
    main()
