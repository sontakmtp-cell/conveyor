# Copilot: Implement strictly per comments.
# Do NOT reference or display the original PDF name or path anywhere in UI or logs.
# Citations must be anonymous: {"page": int, "section": str|None}.
# Build-time uses PDF, runtime uses only the persisted index.

import google.generativeai as genai
import numpy as np
from typing import List
import os
from sentence_transformers import SentenceTransformer

class Embedder:
    def __init__(self, api_key: str = None):
        # If no api_key provided, try to get from environment
        if not api_key:
            api_key = os.getenv('AI_API_KEY')
        
        if not api_key:
            raise ValueError(
                "No API_KEY found for Embedder. Please either:\n"
                "- Set the `AI_API_KEY` environment variable\n"
                "- Pass the key directly to Embedder(api_key=your_key)\n"
                "- Or ensure env_config.txt contains AI_API_KEY=your_key"
            )
        
        try:
            genai.configure(api_key=api_key)
            # Use SentenceTransformer for embeddings
            self.embed_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')  # Multilingual model for Vietnamese support
            self.genai_model = genai.GenerativeModel('gemini-2.0-flash')
            print(f"✅ Embedder initialized successfully with API key: {api_key[:10]}...")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Embedder: {str(e)}")
    
    def embed(self, texts: List[str]) -> np.ndarray:
        """
        Embed a list of texts using Sentence Transformer.
        Returns: numpy array of shape (len(texts), embedding_dim)
        """
        # Generate embeddings using Sentence Transformer
        return self.embed_model.encode(texts, convert_to_numpy=True)
