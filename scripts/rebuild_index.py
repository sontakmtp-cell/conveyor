#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để xây dựng lại index cho ứng dụng Conveyor Calculator.
Sử dụng đường dẫn tuyệt đối để tránh lỗi đường dẫn.
"""

import os
import sys
from pathlib import Path
import shutil

# Add parent directory to path so we can import core
sys.path.append(str(Path(__file__).parent.parent))

def main():
    # Get the root directory of the project
    root_dir = Path(__file__).parent.parent.absolute()
    print(f"Root directory: {root_dir}")
    
    # Set environment variables
    os.environ['INDEX_DIR'] = str(root_dir / 'data' / 'index')
    print(f"INDEX_DIR set to: {os.environ['INDEX_DIR']}")
    
    # Check if index directory exists
    index_dir = Path(os.environ['INDEX_DIR'])
    if index_dir.exists():
        print(f"Index directory exists: {index_dir}")
        
        # Check if chunks.faiss exists
        faiss_file = index_dir / 'chunks.faiss'
        if faiss_file.exists():
            print(f"chunks.faiss found: {faiss_file}")
            print("Index appears to be valid.")
            return 0
        else:
            print("chunks.faiss not found. Index is incomplete.")
    else:
        print(f"Index directory does not exist: {index_dir}")
    
    # Create index directory if it doesn't exist
    index_dir.mkdir(parents=True, exist_ok=True)
    print(f"Created index directory: {index_dir}")
    
    # Check if we have source documents
    hidden_dir = root_dir / 'data' / 'hidden'
    if hidden_dir.exists():
        pdf_files = list(hidden_dir.glob('*.pdf'))
        if pdf_files:
            print(f"Found PDF files: {[f.name for f in pdf_files]}")
            
            # Set PDF_PATH to the first PDF found
            pdf_path = str(pdf_files[0])
            os.environ['PDF_PATH'] = pdf_path
            print(f"PDF_PATH set to: {pdf_path}")
            
            # Try to build index
            try:
                from core.rag.pdf_loader import load_pdf_chunks
                from core.rag.index import build_index
                
                print("Loading PDF chunks...")
                chunks = load_pdf_chunks(pdf_path)
                
                print(f"Loaded {len(chunks)} chunks")
                
                print("Building index...")
                build_index(chunks, str(index_dir))
                
                print("Index built successfully!")
                return 0
                
            except Exception as e:
                print(f"Error building index: {e}")
                return 1
        else:
            print("No PDF files found in data/hidden/")
            print("Please place your source PDF documents in data/hidden/ directory")
            return 1
    else:
        print("data/hidden/ directory not found")
        print("Please create data/hidden/ directory and place your source PDF documents there")
        return 1

if __name__ == "__main__":
    sys.exit(main())
