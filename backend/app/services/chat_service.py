"""聊天服务"""

from sqlalchemy.orm import Session
from app.services.agnes_ai import agnes_ai


class ChatService:
    """聊天核心服务"""

    def __init__(self, db: Session):
        self.db = db

    async def reply(self, context: list) -> str:
        """生成 AI 回复"""
        # 构建系统提示词
        messages = [
            {"role": "system", "content": "你是一个专业的智能客服助手。请简洁、准确地回答用户的问题。如果问题不在知识库范围内，建议转接人工客服。"},
        ]
        messages.extend(context[-20:])  # 最近 20 轮上下文

        response = await agnes_ai.chat_completion(messages)
        return response["choices"][0]["message"]["content"]
