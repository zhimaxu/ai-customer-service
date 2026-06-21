"""客服工作台 API"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.schemas.agent import (
    SessionListItem,
    SessionDetailItem,
    ReplyRequest,
    QuickReplyRequest,
    TakeoverRequest,
)
from app.models.session import Session, Message
from app.services.ws_service import manager

router = APIRouter(prefix="/agent/sessions", tags=["agent"])


@router.get("", response_model=list[SessionListItem])
def list_sessions(
    status: Optional[str] = None,
    agent_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """获取会话列表（支持状态和类型过滤）"""
    query = db.query(Session)
    if status:
        query = query.filter(Session.status == status)
    if agent_type:
        query = query.filter(Session.current_agent_type == agent_type)
    query = query.order_by(Session.updated_at.desc()).limit(100)
    return query.all()


@router.get("/{session_id}", response_model=SessionDetailItem)
def get_session_detail(session_id: str, db: Session = Depends(get_db)):
    """获取会话详情"""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.get("/{session_id}/messages")
def get_session_messages(session_id: str, limit: int = 50, db: Session = Depends(get_db)):
    """获取会话消息历史"""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": m.id,
            "sender": m.sender_type,
            "content": m.content,
            "content_type": m.content_type,
            "created_at": m.created_at.isoformat(),
        }
        for m in reversed(messages)
    ]


@router.post("/{session_id}/takeover")
def takeover_session(session_id: str, req: TakeoverRequest = None, db: Session = Depends(get_db)):
    """客服接管会话"""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.status = "human"
    session.current_agent_type = "agent"
    db.commit()

    # Notify via WebSocket
    agent_id = req.agent_id if req else "unknown"
    import asyncio
    try:
        asyncio.get_event_loop().create_task(
            manager.broadcast(session_id, {
                "type": "notification",
                "session_id": session_id,
                "content": f"客服已接管会话",
            })
        )
    except Exception:
        pass

    return {"status": "taken_over", "session_id": session_id}


@router.post("/{session_id}/reply")
async def reply_to_session(session_id: str, req: ReplyRequest, db: Session = Depends(get_db)):
    """客服回复（REST + WebSocket 广播）"""
    msg = Message(session_id=session_id, sender_type="agent", content=req.message)
    db.add(msg)
    session = db.query(Session).filter(Session.id == session_id).first()
    if session:
        session.last_message_at = Message.utcnow()
        session.message_count += 1
    db.commit()

    # Broadcast via WebSocket
    await manager.broadcast(session_id, {
        "type": "message",
        "sender": "agent",
        "content": req.message,
        "created_at": msg.created_at.isoformat() if msg.created_at else None,
    })

    return {"status": "sent", "message_id": msg.id}


@router.post("/{session_id}/quick-reply")
async def quick_reply(session_id: str, req: QuickReplyRequest, db: Session = Depends(get_db)):
    """快捷回复"""
    msg = Message(session_id=session_id, sender_type="agent", content=req.message)
    db.add(msg)
    session = db.query(Session).filter(Session.id == session_id).first()
    if session:
        session.last_message_at = Message.utcnow()
        session.message_count += 1
    db.commit()

    await manager.broadcast(session_id, {
        "type": "message",
        "sender": "agent",
        "content": req.message,
        "created_at": msg.created_at.isoformat() if msg.created_at else None,
        "is_quick_reply": True,
    })

    return {"status": "sent", "message_id": msg.id}


@router.post("/{session_id}/close")
def close_session(session_id: str, db: Session = Depends(get_db)):
    """结束会话"""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.status = "closed"
    db.commit()

    return {"status": "closed", "session_id": session_id}
