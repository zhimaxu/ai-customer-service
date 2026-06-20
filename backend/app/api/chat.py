"""聊天核心 API"""

import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, AsyncGenerator

from app.core.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.services.summarize_service import SummarizeService
from app.models.session import Session as SessionModel, Message

router = APIRouter(prefix="/chat", tags=["chat"])


def _sse_event(event: str, data: str) -> str:
    """Format an SSE event"""
    return f"event: {event}\ndata: {data}\n\n"


def _get_or_create_session(req: ChatRequest, db: Session) -> SessionModel:
    """Get or create a session"""
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

    return session


def _session_to_dict(s: SessionModel) -> dict:
    """Convert Session to dict"""
    return {
        "id": s.id,
        "tenant_id": s.tenant_id,
        "user_id": s.user_id,
        "channel": s.channel,
        "status": s.status,
        "current_agent_type": s.current_agent_type,
        "last_message_at": s.last_message_at.isoformat() if s.last_message_at else None,
        "message_count": s.message_count,
        "created_at": s.created_at.isoformat(),
        "updated_at": s.updated_at.isoformat() if s.updated_at else None,
    }


@router.post("/stream")
async def send_message_stream(
    req: ChatRequest,
    db: Session = Depends(get_db),
):
    """发送消息，SSE 流式返回 AI 回复"""

    async def event_stream() -> AsyncGenerator[str, None]:
        try:
            # 1. 获取或创建会话
            session = _get_or_create_session(req, db)

            # 2. 保存用户消息
            user_msg = Message(
                session_id=session.id,
                sender_type="user",
                content=req.message,
                content_type="text",
            )
            db.add(user_msg)
            db.flush()

            # 3. 获取上下文
            messages = (
                db.query(Message)
                .filter(Message.session_id == session.id)
                .order_by(Message.created_at.desc())
                .limit(SummarizeService.SUMMARIZE_THRESHOLD)
                .all()
            )
            context = [
                {
                    "role": "user" if m.sender_type == "user" else "assistant",
                    "content": m.content,
                }
                for m in reversed(messages)
            ]

            # 4. 发送 session 事件
            yield _sse_event("session", json.dumps({
                "session_id": session.id,
                "user_id": session.user_id,
            }))

            # 5. 调用流式 AI
            service = ChatService(db, tenant_id=session.tenant_id)
            full_reply = ""
            async for chunk in service.reply_stream(context, req.message):
                if isinstance(chunk, dict):
                    choice = chunk.get("choices", [{}])[0]
                    delta = choice.get("delta", {})
                    content = delta.get("content", "")
                else:
                    content = str(chunk)
                    if content.startswith("data:"):
                        try:
                            data = json.loads(content.split("data:", 1)[1].strip())
                            content = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        except (json.JSONDecodeError, IndexError):
                            content = ""

                if content:
                    full_reply += content
                    yield _sse_event("chunk", json.dumps({"content": content}))

            # 6. 保存 AI 回复
            ai_msg = Message(
                session_id=session.id,
                sender_type="assistant",
                content=full_reply,
                content_type="text",
            )
            db.add(ai_msg)

            # 7. 更新会话统计
            session.last_message_at = Message.utcnow()
            session.message_count += 2
            db.commit()

            # 8. 发送完成事件
            yield _sse_event("done", json.dumps({
                "session_id": session.id,
                "message_id": ai_msg.id,
            }))

        except Exception as e:
            yield _sse_event("error", json.dumps({"detail": str(e)}))

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("", response_model=ChatResponse)
async def send_message(req: ChatRequest, db: Session = Depends(get_db)):
    """发送消息，返回完整 AI 回复（非流式）"""
    session = _get_or_create_session(req, db)

    user_msg = Message(session_id=session.id, sender_type="user", content=req.message)
    db.add(user_msg)
    db.flush()

    messages = (
        db.query(Message)
        .filter(Message.session_id == session.id)
        .order_by(Message.created_at.desc())
        .limit(SummarizeService.SUMMARIZE_THRESHOLD)
        .all()
    )
    context = [
        {"role": "user" if m.sender_type == "user" else "assistant", "content": m.content}
        for m in reversed(messages)
    ]

    service = ChatService(db, tenant_id=session.tenant_id)
    reply = await service.reply(context, req.message)

    ai_msg = Message(session_id=session.id, sender_type="assistant", content=reply)
    db.add(ai_msg)
    db.commit()

    return ChatResponse(session_id=session.id, reply=reply)


@router.get("/sessions")
def list_sessions(
    user_id: Optional[str] = None,
    channel: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    """获取会话列表（支持分页和过滤）"""
    query = db.query(SessionModel)

    if user_id:
        query = query.filter(SessionModel.user_id == user_id)
    if channel:
        query = query.filter(SessionModel.channel == channel)
    if status:
        query = query.filter(SessionModel.status == status)

    total = query.count()
    sessions = (
        query.order_by(SessionModel.updated_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "sessions": [_session_to_dict(s) for s in sessions],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/sessions/{session_id}")
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
        "session": _session_to_dict(session),
        "messages": [
            {
                "id": m.id,
                "sender": m.sender_type,
                "content": m.content,
                "content_type": m.content_type,
                "created_at": m.created_at.isoformat(),
            }
            for m in messages
        ],
    }


@router.delete("/sessions/{session_id}")
def close_session(session_id: str, db: Session = Depends(get_db)):
    """关闭会话"""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.status = "closed"
    db.commit()
    return {"status": "closed", "session_id": session_id}
