# Copilot: Implement strictly per comments.
# Do NOT reference or display the original PDF name or path anywhere in UI or logs.
# Citations must be anonymous: {"page": int, "section": str|None}.
# Build-time uses PDF, runtime uses only the persisted index.

import google.generativeai as genai
import numpy as np
from typing import List
from sentence_transformers import SentenceTransformer

class Embedder:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        # Use SentenceTransformer for embeddings
        self.embed_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')  # Multilingual model for Vietnamese support
        self.genai_model = genai.GenerativeModel('gemini-2.0-flash')
    
    def embed(self, texts: List[str]) -> np.ndarray:
        """
        Embed a list of texts using Sentence Transformer.
        Returns: numpy array of shape (len(texts), embedding_dim)
        """
        # Generate embeddings using Sentence Transformer
        return self.embed_model.encode(texts, convert_to_numpy=True)
