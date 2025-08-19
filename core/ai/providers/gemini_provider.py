# Copilot: Implement strictly per comments.
# Do NOT reference or display the original PDF name or path anywhere in UI or logs.
# Citations must be anonymous: {"page": int, "section": str|None}.
# Build-time uses PDF, runtime uses only the persisted index.

import google.generativeai as genai
import numpy as np
from typing import List, Dict
from .base import AIProvider

class GeminiProvider(AIProvider):
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')  # Updated to correct model version
        
    def embed(self, texts: List[str]) -> np.ndarray:
        """
        Embed texts using Sentence Transformer model.
        Returns: numpy array of shape (len(texts), embedding_dim)
        """
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight, efficient model
            return model.encode(texts, convert_to_numpy=True)
        except ImportError:
            # Fallback to simpler embedding if sentence_transformers not installed
            from sklearn.feature_extraction.text import TfidfVectorizer
            vectorizer = TfidfVectorizer(max_features=384)  # Fixed dimensionality
            return vectorizer.fit_transform(texts).toarray()
    
    def chat(self, system: str, messages: List[Dict]) -> str:
        """
        Generate a chat response using Gemini.
        
        Args:
            system: System prompt
            messages: List of {"role": "user"|"assistant", "content": str}
        
        Returns:
            Generated response text
        """
        try:
            # Combine all messages into one prompt
            full_prompt = f"{system}\n\n"
            for msg in messages:
                prefix = "User: " if msg["role"] == "user" else "Assistant: "
                full_prompt += f"{prefix}{msg['content']}\n\n"
            
            # Generate response using the combined prompt
            response = self.model.generate_content(full_prompt)
            
            if response and response.text:
                return response.text
            else:
                return "Xin lỗi, tôi không thể tạo câu trả lời. Vui lòng thử lại."
            
        except Exception as e:
            print(f"Error in chat: {str(e)}")
            return "Xin lỗi, tôi gặp lỗi khi xử lý câu hỏi của bạn. Vui lòng thử lại."
