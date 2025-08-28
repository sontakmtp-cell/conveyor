# Copilot: Implement strictly per comments.
# Do NOT reference or display the original PDF name or path anywhere in UI or logs.
# Citations must be anonymous: {"page": int, "section": str|None}.
# Build-time uses PDF, runtime uses only the persisted index.

# Copilot: Implement strictly per comments.
# Do NOT reference or display the original PDF name or path anywhere in UI or logs.
# Citations must be anonymous: {"page": int, "section": str|None}.
# Build-time uses PDF, runtime uses only the persisted index.

import os
import logging
from typing import List, Dict, Optional
from .providers.gemini_provider import GeminiProvider
from ..rag.index import Retriever, Chunk
import asyncio

SYSTEM_PROMPT = """Bạn là một trợ lý AI chuyên gia về lĩnh vực băng tải công nghiệp, hoạt động như một kỹ sư trưởng dày dạn kinh nghiệm.

**Nhiệm vụ chính của bạn là luôn luôn giao tiếp và trả lời bằng tiếng Việt.**

Bạn có kiến thức chuyên sâu về:
- Thiết kế và tính toán băng tải theo các tiêu chuẩn DIN 22101, CEMA, ISO 5048.
- Các thông số kỹ thuật: lưu lượng, vận tốc, công suất, lực căng, góc nghiêng.
- Lựa chọn thiết bị: băng tải, con lăn, động cơ, ròng rọc.
- Phân tích chi phí và tối ưu hóa hệ thống.

Khi phản hồi, hãy tuân thủ các nguyên tắc sau:
1.  **Hành động như một kỹ sư trưởng:** Đưa ra lời khuyên thực tế, đáng tin cậy và dễ hiểu.
2.  **Phân tích kỹ lưỡng:** Nghiên cứu cẩn thận các yêu cầu để cung cấp giải pháp chi tiết và chính xác.
3.  **Cung cấp công thức:** Nếu liên quan đến tính toán, hãy nêu rõ công thức, giải thích các biến số và đưa ra giá trị cụ thể.
4.  **Tập trung vào thực tiễn:** Nhấn mạnh tính thực tế và khả năng ứng dụng của giải pháp.
5.  **Cảnh báo an toàn:** Nêu rõ các cảnh báo về an toàn khi cần thiết.
6.  **Dựa vào ngữ cảnh:** Trả lời dựa trên thông tin ngữ cảnh được cung cấp. Nếu không đủ thông tin, hãy nói: "Xin lỗi, tôi cần thêm thông tin về... để có thể trả lời chính xác hơn."
"""

def format_citations(chunks: List[tuple[Chunk, float]]) -> List[Dict]:
    """Format citations without revealing source document."""
    return [
        {
            "page": chunk.page,
            "section": chunk.section
        }
        for chunk, _ in chunks
    ]

class _DummyProvider:
    """Fallback provider used when GeminiProvider cannot initialize."""
    def chat(self, system: str, messages: List[Dict]) -> str:
        last_user = next((m.get("content") for m in reversed(messages) if m.get("role") == "user"), "")
        return (
            "AI features are unavailable (missing or invalid API key). "
            "Showing a basic response. Your question was: " + last_user
        )

    async def chat_async(self, system: str, messages: List[Dict]) -> str:
        return self.chat(system, messages)


class ChatService:
    def __init__(self, retriever: Optional[Retriever]):
        self.retriever = retriever
        
        # Initialize AI provider with better error handling
        try:
            self.provider = GeminiProvider()  # Will automatically get API key from environment
            print("ChatService: GeminiProvider initialized successfully")
        except Exception as e:
            # Fallback gracefully without breaking the app
            print(f"ChatService: Failed to initialize GeminiProvider: {e}")
            self.provider = _DummyProvider()
    
    def ask(self, 
            question: str, 
            history: Optional[List[Dict]] = None, 
            top_k: int = 6) -> Dict:
        """
        Answer a question using RAG with enhanced context processing.
        
        Args:
            question: User's question
            history: Optional chat history [{"role": "user"|"assistant", "content": str}]
            top_k: Number of chunks to retrieve
            
        Returns:
            {
                "answer": str
            }
        """
        try:
            # Check if RAG is available
            if self.retriever is None:
                # Fallback to basic chat without RAG
                messages = history or []
                messages.append({"role": "user", "content": question})
                
                answer = self.provider.chat(SYSTEM_PROMPT, messages)
                return {
                    "answer": answer
                }
            
            # Analyze question type
            tech_keywords = ["formula", "calculation", "design", "parameter", "standard", 
                           "conveyor", "motor", "roller", "pulley", "optimization"]
            is_technical = any(keyword in question.lower() for keyword in tech_keywords)
            
            # Retrieve relevant chunks with adjusted top_k
            if is_technical:
                # Technical questions need more context
                chunks = self.retriever.search(question, top_k + 2)
            else:
                chunks = self.retriever.search(question, top_k)
            
            if not chunks:
                return {
                    "answer": "Sorry, I could not find relevant information to answer your question."
                }
            
            # Sort chunks by relevance score
            chunks.sort(key=lambda x: x[1], reverse=True)
            
            # Build enhanced context
            technical_context = []
            general_context = []
            
            for chunk, score in chunks:
                if any(keyword in chunk.text.lower() for keyword in tech_keywords):
                    technical_context.append(chunk.text)
                else:
                    general_context.append(chunk.text)
            
            # Combine context with technical information first
            context = "\n\n".join(technical_context + general_context)
            
            # Build enhanced prompt
            prompt = f"""Based on the following professional information to answer the question.
If the answer relates to technical calculations, please:
1. Explain important concepts
2. Provide calculation formulas if any
3. Propose reference values or appropriate ranges
4. State notes when applying

Reference information:
{context}

User question: {question}"""
            
            # Get chat history or initialize if none
            messages = history or []
            messages.append({"role": "user", "content": prompt})
            
            # Generate response
            answer = self.provider.chat(SYSTEM_PROMPT, messages)
            
            return {
                "answer": answer
            }
            
        except Exception as e:
            import traceback
            error_details = f"Error in ChatService: {str(e)}\nTraceback: {traceback.format_exc()}"
            print(error_details)
            logging.error(error_details)
            return {
                "answer": f"Sorry, I encountered an error while processing your question: {str(e)}. Please try again."
            }

    async def ask_async(self, 
            question: str, 
            history: Optional[List[Dict]] = None, 
            top_k: int = 6) -> Dict:
        """
        Asynchronously answer a question using RAG.
        """
        try:
            if self.retriever is None:
                messages = history or []
                messages.append({"role": "user", "content": question})
                answer = await self.provider.chat_async(SYSTEM_PROMPT, messages)
                return {"answer": answer}

            tech_keywords = ["formula", "calculation", "design", "parameter", "standard", 
                           "conveyor", "motor", "roller", "pulley", "optimization"]
            is_technical = any(keyword in question.lower() for keyword in tech_keywords)
            
            chunks = self.retriever.search(question, top_k + 2 if is_technical else top_k)
            
            if not chunks:
                return {"answer": "Sorry, I could not find relevant information to answer your question."}
            
            chunks.sort(key=lambda x: x[1], reverse=True)
            
            technical_context = [chunk.text for chunk, score in chunks if any(keyword in chunk.text.lower() for keyword in tech_keywords)]
            general_context = [chunk.text for chunk, score in chunks if not any(keyword in chunk.text.lower() for keyword in tech_keywords)]
            
            context = "\n\n".join(technical_context + general_context)
            
            prompt = f"""Based on the following professional information to answer the question.
If the answer relates to technical calculations, please:
1. Explain important concepts
2. Provide calculation formulas if any
3. Propose reference values or appropriate ranges
4. State notes when applying

Reference information:
{context}

User question: {question}"""
            
            messages = history or []
            messages.append({"role": "user", "content": prompt})
            
            answer = await self.provider.chat_async(SYSTEM_PROMPT, messages)
            
            return {"answer": answer}
            
        except Exception as e:
            import traceback
            error_details = f"Error in ChatService.ask_async: {str(e)}\nTraceback: {traceback.format_exc()}"
            print(error_details)
            logging.error(error_details)
            return {"answer": f"Sorry, I encountered an error while processing your question: {str(e)}. Please try again."}
