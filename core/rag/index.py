# Copilot: Implement strictly per comments.
# Do NOT reference or display the original PDF name or path anywhere in UI or logs.
# Citations must be anonymous: {"page": int, "section": str|None}.
# Build-time uses PDF, runtime uses only the persisted index.

import json
import os
import faiss
import numpy as np
from typing import List, Tuple
from .schema import Chunk
from .embedder import Embedder

class Retriever:
    def __init__(self, index: faiss.Index, chunks: List[Chunk]):
        self.index = index
        self.chunks = chunks
    
    def search(self, query: str, top_k: int) -> List[Tuple[Chunk, float]]:
        """Search for most similar chunks to the query."""
        # Get query embedding
        embedder = Embedder(os.getenv('AI_API_KEY'))
        query_embedding = embedder.embed([query])[0]
        
        # Search in the FAISS index
        scores, indices = self.index.search(query_embedding.reshape(1, -1), top_k)
        
        # Return chunks with their scores
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0:  # Valid index
                results.append((self.chunks[idx], float(score)))
        return results

def build_index(chunks: List[Chunk], out_dir: str) -> None:
    """Build and save FAISS index and chunk metadata."""
    # Create embeddings
    embedder = Embedder(os.getenv('AI_API_KEY'))
    texts = [chunk.text for chunk in chunks]
    embeddings = embedder.embed(texts)
    
    # Build FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)  # Inner product similarity
    index.add(embeddings)
    
    # Save index
    os.makedirs(out_dir, exist_ok=True)
    faiss.write_index(index, os.path.join(out_dir, "chunks.faiss"))
    
    # Save chunks metadata
    chunks_data = [
        {
            "id": chunk.id,
            "page": chunk.page,
            "section": chunk.section,
            "kind": chunk.kind,
            "text": chunk.text
        }
        for chunk in chunks
    ]
    with open(os.path.join(out_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(chunks_data, f, ensure_ascii=False, indent=2)

def load_index(in_dir: str) -> Retriever:
    """Load saved index and chunks."""
    # Load FAISS index
    index = faiss.read_index(os.path.join(in_dir, "chunks.faiss"))
    
    # Load chunks
    with open(os.path.join(in_dir, "manifest.json"), "r", encoding="utf-8") as f:
        chunks_data = json.load(f)
    
    chunks = [
        Chunk(
            id=data["id"],
            text=data["text"],
            page=data["page"],
            section=data["section"],
            kind=data["kind"]
        )
        for data in chunks_data
    ]
    
    return Retriever(index, chunks)
