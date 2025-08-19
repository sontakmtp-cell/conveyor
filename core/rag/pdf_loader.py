# Copilot: Implement strictly per comments.
# Do NOT reference or display the original PDF name or path anywhere in UI or logs.
# Citations must be anonymous: {"page": int, "section": str|None}.
# Build-time uses PDF, runtime uses only the persisted index.

import fitz  # PyMuPDF
import re
import uuid
from typing import List
from .schema import Chunk

def detect_content_type(text: str) -> str:
    """Detect if text is a table, equation, or normal text."""
    # Simple heuristic - can be improved
    if re.search(r'[=+\-*/]\s*\d', text) and len(text.split('\n')) < 3:
        return "equation"
    if '|' in text or '\t' in text:
        return "table"
    return "text"

def extract_section_title(text: str) -> str | None:
    """Extract section title from text if it exists."""
    lines = text.strip().split('\n')
    if lines and re.match(r'^\d+\.[\d\.]*\s+\w+', lines[0]):
        return lines[0]
    return None

def load_pdf_chunks(pdf_path: str) -> List[Chunk]:
    """Read PDF and split into chunks while preserving equations and tables."""
    chunks = []
    doc = fitz.open(pdf_path)
    
    current_section = None
    buffer = []
    buffer_type = "text"
    
    for page in doc:
        page_text = page.get_text()
        blocks = page.get_text("blocks")
        
        for block in blocks:
            text = block[4].strip()
            if not text:
                continue
                
            # Check for section title
            section = extract_section_title(text)
            if section:
                current_section = section
                continue
                
            content_type = detect_content_type(text)
            
            # If we hit a special content type or buffer is getting too large
            if (content_type != buffer_type) or (len(''.join(buffer)) > 800):
                if buffer:
                    chunks.append(Chunk(
                        id=str(uuid.uuid4()),
                        text='\n'.join(buffer),
                        page=page.number + 1,
                        section=current_section,
                        kind=buffer_type
                    ))
                    buffer = []
                
            buffer.append(text)
            buffer_type = content_type
            
        # Flush buffer at end of page
        if buffer:
            chunks.append(Chunk(
                id=str(uuid.uuid4()),
                text='\n'.join(buffer),
                page=page.number + 1,
                section=current_section,
                kind=buffer_type
            ))
            buffer = []
            
    doc.close()
    return chunks
