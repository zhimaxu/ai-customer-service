"""WebSocket API for agent workspace real-time push"""

import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.session import Session as SessionModel, Message
from app.services.ws_service import manager

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str, db: Session = Depends(get_db)):
    """
    WebSocket endpoint for agent workspace.

    Protocol: JSON messages over WebSocket.

    Client -> Server messages:
    - {"type": "reply", "content": "message text"}  -- agent reply
    - {"type": "takeover", "agent_id": "xxx"}        -- agent takeover
    - {"type": "heartbeat"}                          -- heartbeat ping

    Server -> Client messages:
    - {"type": "message", "sender": "user/assistant", "content": "...", "created_at": "..."}
    - {"type": "notification", "session_id": "...", "content": "..."}
    - {"type": "pong"}
    """
    # Verify session exists
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        await websocket.close(code=4004, reason="Session not found")
        return

    await manager.connect(websocket, session_id)

    try:
        while True:
            raw = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"type": "error", "detail": "Invalid JSON"}))
                continue

            msg_type = data.get("type", "")

            if msg_type == "heartbeat":
                await websocket.send_text(json.dumps({"type": "pong"}))

            elif msg_type == "reply":
                content = data.get("content", "")
                if not content:
                    await websocket.send_text(json.dumps({"type": "error", "detail": "Empty content"}))
                    continue

                # Save agent reply to DB
                agent_msg = Message(
                    session_id=session_id,
                    sender_type="agent",
                    content=content,
                    content_type="text",
                )
                db.add(agent_msg)
                session.last_message_at = Message.utcnow()
                session.message_count += 1
                session.current_agent_type = "agent"
                db.commit()

                # Broadcast to all clients in this session
                await manager.broadcast(session_id, {
                    "type": "message",
                    "sender": "agent",
                    "content": content,
                    "created_at": agent_msg.created_at.isoformat() if agent_msg.created_at else None,
                })

            elif msg_type == "takeover":
                agent_id = data.get("agent_id", "unknown")
                session.current_agent_type = "agent"
                session.status = "human"
                db.commit()

                await manager.broadcast(session_id, {
                    "type": "notification",
                    "session_id": session_id,
                    "content": f"Agent took over session (agent_id: {agent_id})",
                })

            else:
                await websocket.send_text(json.dumps({"type": "error", "detail": f"Unknown type: {msg_type}"}))

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except asyncio.TimeoutError:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)


@router.websocket("/ws/agent")
async def websocket_agent(websocket: WebSocket):
    """
    Global WebSocket for agent to receive notifications across all sessions.
    """
    await websocket.accept()
    await manager.connect(websocket, "__agent_global__")

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                continue

            if data.get("type") == "heartbeat":
                await websocket.send_text(json.dumps({"type": "pong"}))

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)
