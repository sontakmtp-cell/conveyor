# Copilot: Implement strictly per comments.
# Do NOT reference or display the original PDF name or path anywhere in UI or logs.
# Citations must be anonymous: {"page": int, "section": str|None}.
# Build-time uses PDF, runtime uses only the persisted index.

import os
from typing import List, Dict, Optional
from .providers.gemini_provider import GeminiProvider
from ..rag.index import Retriever, Chunk

SYSTEM_PROMPT = """
Bạn là một chuyên gia kỹ thuật về băng tải công nghiệp với kiến thức chuyên sâu về:
- Thiết kế và tính toán băng tải theo tiêu chuẩn DIN 22101, CEMA, ISO 5048
- Các thông số kỹ thuật: lưu lượng, tốc độ, công suất, lực căng, góc nghiêng
- Lựa chọn thiết bị: băng tải, con lăn, động cơ, puly
- Phân tích chi phí và tối ưu hóa hệ thống

Khi trả lời:
1. Phân tích kỹ yêu cầu và đưa ra giải pháp chi tiết
2. Nếu liên quan đến tính toán, cung cấp công thức và giá trị cụ thể
3. Giải thích các khuyến nghị kỹ thuật một cách dễ hiểu
4. Tập trung vào tính thực tiễn và áp dụng được
5. Nêu rõ các cảnh báo an toàn khi cần thiết

Trả lời dựa trên context được cung cấp. Nếu không đủ thông tin, hãy nói "Xin lỗi, tôi cần thêm thông tin về... để trả lời chính xác hơn."
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

class ChatService:
    def __init__(self, retriever: Optional[Retriever]):
        self.retriever = retriever
        self.provider = GeminiProvider(os.getenv('AI_API_KEY'))
    
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
            tech_keywords = ["công thức", "tính toán", "thiết kế", "thông số", "tiêu chuẩn", 
                           "băng tải", "động cơ", "con lăn", "puly", "tối ưu"]
            is_technical = any(keyword in question.lower() for keyword in tech_keywords)
            
            # Retrieve relevant chunks with adjusted top_k
            if is_technical:
                # Technical questions need more context
                chunks = self.retriever.search(question, top_k + 2)
            else:
                chunks = self.retriever.search(question, top_k)
            
            if not chunks:
                return {
                    "answer": "Xin lỗi, tôi không tìm thấy thông tin liên quan để trả lời câu hỏi của bạn."
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
            prompt = f"""Dựa trên thông tin chuyên môn sau đây để trả lời câu hỏi.
Nếu câu trả lời liên quan đến tính toán kỹ thuật, hãy:
1. Giải thích các khái niệm quan trọng
2. Cung cấp công thức tính toán nếu có
3. Đề xuất các giá trị tham khảo hoặc phạm vi phù hợp
4. Nêu các lưu ý khi áp dụng

Thông tin tham khảo:
{context}

Câu hỏi của người dùng: {question}"""
            
            # Get chat history or initialize if none
            messages = history or []
            messages.append({"role": "user", "content": prompt})
            
            # Generate response
            answer = self.provider.chat(SYSTEM_PROMPT, messages)
            
            return {
                "answer": answer
            }
            
        except Exception as e:
            print(f"Error in ChatService: {str(e)}")
            return {
                "answer": "Xin lỗi, tôi gặp lỗi khi xử lý câu hỏi của bạn. Vui lòng thử lại."
            }
