# Copilot: Implement strictly per comments.
# Do NOT reference or display the original PDF name or path anywhere in UI or logs.
# Citations must be anonymous: {"page": int, "section": str|None}.
# Build-time uses PDF, runtime uses only the persisted index.

from abc import ABC, abstractmethod
from typing import List, Dict
import numpy as np

class AIProvider(ABC):
    @abstractmethod
    def embed(self, texts: List[str]) -> np.ndarray:
        """Embed a list of texts into vectors."""
        pass
    
    @abstractmethod
    def chat(self, system: str, messages: List[Dict]) -> str:
        """Generate a chat response given system prompt and message history."""
        pass
