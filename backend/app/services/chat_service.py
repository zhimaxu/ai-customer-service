"""聊天核心服务"""

from sqlalchemy.orm import Session
from app.services.agnes_ai import agnes_ai
from app.services.rag_service import RAGService
from app.services.summarize_service import SummarizeService


class ChatService:
    """聊天核心服务 — RAG + 滑动窗口 + 动态摘要"""

    SYSTEM_PROMPT = (
        "你是一个专业的智能客服助手。请简洁、准确地回答用户的问题。"
        "如果问题不在知识库范围内，建议转接人工客服。"
    )

    def __init__(self, db: Session, tenant_id: str = "default"):
        self.db = db
        self.tenant_id = tenant_id

    async def _build_prompt(self, context: list, user_message: str) -> tuple:
        """
        Build the full prompt with RAG context and summarization.
        Returns (messages_list, rag_hit_count).
        """
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
        ]

        # Step 1: RAG retrieval
        rag_service = RAGService(tenant_id=self.tenant_id)
        snippets = await rag_service.retrieve(user_message)
        if snippets:
            knowledge_context = "\n".join(f"片段{i+1}: {s}" for i, s in enumerate(snippets))
            messages.append({
                "role": "system",
                "content": f"以下是相关知识库内容，供参考回答用户问题：\n{knowledge_context}\n如果知识库中没有相关内容，请告知用户并建议转人工。",
            })

        # Step 2: Summarize early messages if window exceeded
        summary = await SummarizeService.summarize_early_messages(context)
        if summary:
            messages.append({"role": "system", "content": summary})

        # Step 3: Add sliding window messages
        recent = context[-SummarizeService.WINDOW_SIZE:]
        messages.extend(recent)

        return messages, len(snippets)

    async def reply(self, context: list, user_message: str = "") -> str:
        """Generate AI reply (non-streaming)"""
        messages, _ = await self._build_prompt(context, user_message)
        response = await agnes_ai.chat_completion(messages)
        return response["choices"][0]["message"]["content"]

    async def reply_stream(self, context: list, user_message: str = ""):
        """Generate AI reply (streaming generator for SSE)"""
        messages, _ = await self._build_prompt(context, user_message)
        response = await agnes_ai.chat_stream(messages, stream=True)

        if hasattr(response, "__aiter__"):
            async for chunk in response:
                yield chunk
        elif isinstance(response, dict):
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            yield content
