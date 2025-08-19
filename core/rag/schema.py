# Copilot: Implement strictly per comments.
# Do NOT reference or display the original PDF name or path anywhere in UI or logs.
# Citations must be anonymous: {"page": int, "section": str|None}.
# Build-time uses PDF, runtime uses only the persisted index.

from dataclasses import dataclass

@dataclass
class Chunk:
    id: str
    text: str
    page: int
    section: str | None
    kind: str | None  # "text" | "table" | "equation"
