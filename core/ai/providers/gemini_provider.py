# Copilot: Implement strictly per comments.
# Do NOT reference or display the original PDF name or path anywhere in UI or logs.
# Citations must be anonymous: {"page": int, "section": str|None}.
# Build-time uses PDF, runtime uses only the persisted index.

import google.generativeai as genai
import numpy as np
from typing import List, Dict
import os
import sys
from .base import AIProvider
import asyncio

def _get_root_dir():
    """Gets the application root directory, works for dev and for PyInstaller."""
    if getattr(sys, 'frozen', False):
        # Running in a bundle
        return os.path.dirname(sys.executable)
    else:
        # Running in a normal Python environment, go up 3 levels
        return os.path.abspath(os.path.join(os.path.dirname(__file__), '..\..\..'))

class GeminiProvider(AIProvider):
    def __init__(self, api_key: str = None):
        if not api_key:
            api_key = os.getenv('AI_API_KEY')
        
        if not api_key:
            # Do not show modal dialogs or exit the app here. Propagate up.
            raise RuntimeError("AI_API_KEY is missing. Cannot initialize GeminiProvider.")
        
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            print(f"GeminiProvider initialized successfully with API key: {api_key[:10]}...")
        except Exception as e:
            # Do not display dialogs or exit; allow caller to handle gracefully
            msg = str(e)
            if "API key not valid" in msg or "invalid" in msg.lower():
                raise RuntimeError("Invalid AI API key for GeminiProvider")
            raise RuntimeError(f"Failed to initialize Gemini API: {msg}")
        
    def embed(self, texts: List[str]) -> np.ndarray:
        """
        Embed texts using Sentence Transformer model.
        Returns: numpy array of shape (len(texts), embedding_dim)
        """
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('all-MiniLM-L6-v2')
            return model.encode(texts, convert_to_numpy=True)
        except ImportError:
            from sklearn.feature_extraction.text import TfidfVectorizer
            vectorizer = TfidfVectorizer(max_features=384)
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
            full_prompt = f"{system}\n\n"
            for msg in messages:
                prefix = "User: " if msg["role"] == "user" else "Assistant: "
                full_prompt += f"{prefix}{msg['content']}\n\n"
            
            response = self.model.generate_content(full_prompt)
            
            if response and response.text:
                return response.text
            else:
                return "Sorry, I could not generate a response. Please try again."
            
        except Exception as e:
            import traceback
            error_details = f"Error in GeminiProvider.chat: {str(e)}\nTraceback: {traceback.format_exc()}"
            print(error_details)
            return f"Sorry, I encountered an error while processing your question: {str(e)}. Please try again."

    async def chat_async(self, system: str, messages: List[Dict]) -> str:
        """
        Asynchronously generate a chat response using Gemini.
        """
        try:
            full_prompt = f"{system}\n\n"
            for msg in messages:
                prefix = "User: " if msg["role"] == "user" else "Assistant: "
                full_prompt += f"{prefix}{msg['content']}\n\n"
            
            response = await self.model.generate_content_async(full_prompt)
            
            if response and response.text:
                return response.text
            else:
                return "Sorry, I could not generate a response. Please try again."
            
        except Exception as e:
            import traceback
            error_details = f"Error in GeminiProvider.chat_async: {str(e)}\nTraceback: {traceback.format_exc()}"
            print(error_details)
            return f"Sorry, I encountered an error while processing your question: {str(e)}. Please try again."
