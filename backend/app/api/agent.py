"""客服工作台 API"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.agent import SessionListItem, ReplyRequest

router = APIRouter(prefix="/agent/sessions", tags=["agent"])


@router.get("", response_model=list[SessionListItem])
def list_sessions(db: Session = Depends(get_db)):
    """获取会话列表"""
    from app.models.session import Session

    sessions = (
        db.query(Session)
        .filter(Session.status == "active")
        .order_by(Session.updated_at.desc())
        .limit(50)
        .all()
    )
    return sessions


@router.post("/{session_id}/takeover")
def takeover_session(session_id: str, db: Session = Depends(get_db)):
    """客服接管会话"""
    from app.models.session import Session

    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.status = "human"
    session.current_agent_type = "agent"
    db.commit()
    return {"status": "taken_over", "session_id": session_id}


@router.post("/{session_id}/reply")
def reply_to_session(session_id: str, req: ReplyRequest, db: Session = Depends(get_db)):
    """客服回复"""
    from app.models.message import Message

    msg = Message(session_id=session_id, sender_type="agent", content=req.message)
    db.add(msg)
    db.commit()
    return {"status": "sent"}


@router.post("/{session_id}/close")
def close_session(session_id: str, db: Session = Depends(get_db)):
    """结束会话"""
    from app.models.session import Session

    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.status = "closed"
    db.commit()
    return {"status": "closed"}
