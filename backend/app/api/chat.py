"""聊天核心 API"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.models.session import Session as SessionModel, Message

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def send_message(req: ChatRequest, db: Session = Depends(get_db)):
    """发送消息，返回 AI 回复"""
    # 获取或创建会话
    if req.session_id:
        session = db.query(SessionModel).filter(SessionModel.id == req.session_id).first()
    else:
        session = None

    if not session:
        session = SessionModel(
            tenant_id=req.tenant_id or "default",
            user_id=req.user_id or "anonymous",
            channel=req.channel or "web",
        )
        db.add(session)
        db.commit()
        db.refresh(session)

    # 保存用户消息
    user_msg = Message(session_id=session.id, sender_type="user", content=req.message)
    db.add(user_msg)
    db.flush()

    # 获取上下文
    messages = (
        db.query(Message)
        .filter(Message.session_id == session.id)
        .order_by(Message.created_at.desc())
        .limit(20)
        .all()
    )
    context = [
        {"role": "user" if m.sender_type == "user" else "assistant", "content": m.content}
        for m in reversed(messages)
    ]

    # 调用 Agnes AI
    service = ChatService(db)
    reply = await service.reply(context)

    # 保存 AI 回复
    ai_msg = Message(session_id=session.id, sender_type="assistant", content=reply)
    db.add(ai_msg)
    db.commit()

    return ChatResponse(session_id=session.id, reply=reply)


@router.get("/{session_id}")
def get_session(session_id: str, db: Session = Depends(get_db)):
    """获取会话详情"""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.created_at.asc())
        .all()
    )
    return {
        "session": session,
        "messages": [
            {"sender": m.sender_type, "content": m.content, "created_at": m.created_at}
            for m in messages
        ],
    }
