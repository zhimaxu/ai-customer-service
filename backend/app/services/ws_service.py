"""WebSocket 连接管理器 — 客服工作台实时推送"""

from typing import Dict, Set
from fastapi import WebSocket


class ConnectionManager:
    """管理 WebSocket 连接和消息广播"""

    def __init__(self):
        # session_id -> set of websockets
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # websocket -> session_id mapping
        self.websocket_to_session: Dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        """接受 WebSocket 连接并加入会话组"""
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        self.active_connections[session_id].add(websocket)
        self.websocket_to_session[websocket] = session_id

    def disconnect(self, websocket: WebSocket):
        """移除 WebSocket 连接"""
        session_id = self.websocket_to_session.get(websocket)
        if session_id and session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        self.websocket_to_session.pop(websocket, None)

    async def broadcast(self, session_id: str, message: dict):
        """向指定会话的所有 WebSocket 发送消息"""
        if session_id in self.active_connections:
            import json
            data = json.dumps(message, ensure_ascii=False)
            disconnected = set()
            for ws in self.active_connections[session_id]:
                try:
                    await ws.send_text(data)
                except Exception:
                    disconnected.add(ws)
            for ws in disconnected:
                self.disconnect(ws)

    async def broadcast_to_all(self, message: dict):
        """向所有连接的客服发送消息"""
        import json
        data = json.dumps(message, ensure_ascii=False)
        for session_id in list(self.active_connections.keys()):
            disconnected = set()
            for ws in self.active_connections[session_id]:
                try:
                    await ws.send_text(data)
                except Exception:
                    disconnected.add(ws)
            for ws in disconnected:
                self.disconnect(ws)


# 全局单例
manager = ConnectionManager()
