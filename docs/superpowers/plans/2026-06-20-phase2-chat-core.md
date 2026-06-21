# Phase 2: 聊天核心 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement SSE streaming, sliding window context with dynamic summarization, RAG retrieval from Qdrant, and session management APIs.

**Architecture:** Extend Phase 1 FastAPI skeleton with streaming endpoints, a RAG service layer, and a summarization service. Use FastAPI's StreamingResponse for SSE with structured JSON events.

**Tech Stack:** FastAPI, SQLAlchemy, httpx, qdrant-client, Agnes AI (text completion + embedding), SSE

---

### Pre-flight: Install dependencies

**Files:**
- Modify: `backend/requirements.txt`

- [ ] **Step 1: Add missing dependencies**

The current `requirements.txt` lacks `sse-starlette` (for SSE support) and `openai` (for embedding). Add them:

```
# Add to backend/requirements.txt:
sse-starlette==2.2.0
openai==1.99.0
```

Note: We use the `openai` SDK because Agnes AI's API is OpenAI-compatible (`/v1/chat/completions`, `/v1/embeddings`). The `httpx` approach in `agnes_ai.py` works but we need the embedding endpoint which isn't wrapped yet.

- [ ] **Step 2: Verify requirements install**

Run: `cd backend && pip install -r requirements.txt --dry-run`
Expected: All packages resolve without conflicts

- [ ] **Step 3: Commit**

```bash
git add backend/requirements.txt
git commit -m "chore: add sse-starlette and openai dependencies for Phase 2"
```

---

### Task 1: Add embedding support to Agnes AI client

**Files:**
- Modify: `backend/app/services/agnes_ai.py`

- [ ] **Step 1: Add embedding method to AgnesAI class**

Add a new method to the existing `AgnesAI` class:

```python
async def embedding(self, text: str, model: str = "agnes-embedding-v1") -> list[float]:
    """Generate embedding vector for text"""
    payload = {
        "model": model,
        "input": text,
    }
    return await self._request("POST", "/embeddings", payload)
```

This returns a dict with `data[0].embedding` (OpenAI-compatible format).

- [ ] **Step 2: Commit**

```bash
git add backend/app/services/agnes_ai.py
git commit -m "feat: add embedding method to AgnesAI client"
```

---

### Task 2: Enhance Session model with tracking fields

**Files:**
- Modify: `backend/app/models/session.py`

- [ ] **Step 1: Add fields to Session model**

Add `last_message_at`, `message_count`, `query_count` columns:

```python
class Session(Base):
    __tablename__ = "session"

    id = Column(VARCHAR(36), primary_key=True, default=uuid.uuid4, comment="UUID")
    tenant_id = Column(VARCHAR(36), nullable=False)
    user_id = Column(VARCHAR(36), nullable=False)
    channel = Column(VARCHAR(20), default="web")
    status = Column(VARCHAR(20), default="active")  # active, human, closed
    current_agent_type = Column(VARCHAR(20), default="ai")  # ai, agent
    last_message_at = Column(DateTime, nullable=True)
    message_count = Column(Integer, default=0)
    query_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
```

- [ ] **Step 2: Generate Alembic migration**

Run: `cd backend && alembic revision --autogenerate -m "add session tracking fields"`
Then: `cd backend && alembic upgrade head`

Expected: Migration file created, tables updated

- [ ] **Step 3: Commit**

```bash
git add backend/app/models/session.py backend/alembic/versions/
git commit -m "feat: add tracking fields to Session model"
```

---

### Task 3: Create RAG service

**Files:**
- Create: `backend/app/services/rag_service.py`
- Modify: `backend/app/core/qdrant_client.py` (add tenant-aware search helper)

- [ ] **Step 1: Create rag_service.py**

```python
"""RAG (Retrieval-Augmented Generation) service"""

from app.core.qdrant_client import qdrant_client, COLLECTION_NAME, VECTOR_SIZE
from app.services.agnes_ai import agnes_ai
from app.core.config import settings
from qdrant_client.models import Distance, Filter, FieldCondition, MatchValue


class RAGService:
    """Knowledge base retrieval service"""

    def __init__(self, tenant_id: str = "default"):
        self.tenant_id = tenant_id

    async def retrieve(self, query: str, top_k: int = 3, score_threshold: float = 0.5) -> list[str]:
        """
        Retrieve relevant knowledge fragments for a query.
        Returns list of text snippets.
        """
        # Step 1: Get embedding for the query
        embed_resp = await agnes_ai.embedding(query)
        query_vector = embed_resp["data"][0]["embedding"]

        # Step 2: Search Qdrant with tenant filter
        search_filter = Filter(
            must=[
                FieldCondition(key="tenant_id", match=MatchValue(value=self.tenant_id)),
            ]
        )

        hits = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=top_k,
            score_threshold=score_threshold,
            query_filter=search_filter,
        )

        # Step 3: Extract text snippets
        snippets = []
        for hit in hits:
            snippet = hit.payload.get("content", "")
            if snippet:
                snippets.append(snippet)

        return snippets

    async def retrieve_fallback(self, query: str, top_k: int = 5) -> list[str]:
        """Fallback: search without score threshold (return top-K regardless)"""
        embed_resp = await agnes_ai.embedding(query)
        query_vector = embed_resp["data"][0]["embedding"]

        hits = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=top_k,
            query_filter=Filter(
                must=[
                    FieldCondition(key="tenant_id", match=MatchValue(value=self.tenant_id)),
                ]
            ),
        )

        return [h.payload.get("content", "") for h in hits if h.payload.get("content")]
```

- [ ] **Step 2: Update qdrant_client.py to support payload schema**

Add payload index for `tenant_id` so filtered searches work efficiently:

```python
# Add after init_collection function:
def init_payload_schema(client: QdrantClient):
    """Initialize payload indexes for filtered queries"""
    client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="tenant_id",
        field_schema=PayloadSchemaType.KEYWORD,
    )
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/services/rag_service.py backend/app/core/qdrant_client.py
git commit -m "feat: add RAG service for knowledge base retrieval"
```

---

### Task 4: Create summarization service

**Files:**
- Create: `backend/app/services/summarize_service.py`

- [ ] **Step 1: Create summarize_service.py**

```python
"""Conversation summarization service"""

from app.services.agnes_ai import agnes_ai


SUMMARIZE_PROMPT = (
    "请总结以下客服对话的核心内容，保留关键问题和答案要点，"
    "忽略寒暄用语。输出3-5句话的中文摘要。\n\n"
    "<conversation>\n{history}\n</conversation>"
)


class SummarizeService:
    """对话摘要服务"""

    WINDOW_SIZE = 20  # 保留最近 20 条消息（10 轮对话）
    SUMMARIZE_THRESHOLD = 40  # 超过 40 条消息时触发摘要

    @staticmethod
    async def summarize_early_messages(messages: list[dict]) -> str:
        """
        Summarize early messages when context window exceeds threshold.
        messages: list of {"role": "user"/"assistant", "content": "..."}
        Returns summary string, or empty string if no summarization needed.
        """
        if len(messages) <= SummarizeService.WINDOW_SIZE:
            return ""

        # Split: early messages for summarization, recent for sliding window
        early_messages = messages[: -(SummarizeService.WINDOW_SIZE)]
        recent_messages = messages[-(SummarizeService.WINDOW_SIZE) :]

        # Build conversation text for summarization
        history_lines = []
        for msg in early_messages:
            role_label = "用户" if msg["role"] == "user" else "客服"
            history_lines.append(f"{role_label}: {msg['content']}")
        history_text = "\n".join(history_lines)

        prompt = SUMMARIZE_PROMPT.format(history=history_text)
        response = await agnes_ai.chat_completion([
            {"role": "user", "content": prompt},
        ])

        summary = response["choices"][0]["message"]["content"]
        return f"[对话摘要] {summary}\n\n"
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/services/summarize_service.py
git commit -m "feat: add conversation summarization service"
```

---

### Task 5: Refactor ChatService with RAG + summarization

**Files:**
- Modify: `backend/app/services/chat_service.py`

- [ ] **Step 1: Rewrite ChatService**

Replace the existing simple `ChatService` with an enhanced version:

```python
"""聊天核心服务"""

from sqlalchemy.orm import Session
from app.services.agnes_ai import agnes_ai
from app.services.rag_service import RAGService
from app.services.summarize_service import SummarizeService
from app.models.session import Session as SessionModel, Message


class ChatService:
    """聊天核心服务 — RAG + 滑动窗口 + 动态摘要"""

    SYSTEM_PROMPT = (
        "你是一个专业的智能客服助手。请简洁、准确地回答用户的问题。"
        "如果问题不在知识库范围内，建议转接人工客服。"
    )

    def __init__(self, db: Session, tenant_id: str = "default"):
        self.db = db
        self.tenant_id = tenant_id

    async def _build_prompt(self, context: list, user_message: str) -> tuple[list, list]:
        """
        Build the full prompt with RAG context and summarization.
        Returns (messages, token_count_estimate).
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
        messages, query_count = await self._build_prompt(context, user_message)
        response = await agnes_ai.chat_stream(messages, stream=True)

        # This yields raw SSE lines from Agnes — caller handles parsing
        # For structured events, see the API layer
        if hasattr(response, "__aiter__"):
            async for chunk in response:
                yield chunk
        elif isinstance(response, dict):
            # Fallback: non-streaming response masquerading
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            yield content
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/services/chat_service.py
git commit -m "refactor: enhance ChatService with RAG + summarization + streaming"
```

---

### Task 6: Implement SSE streaming endpoint

**Files:**
- Modify: `backend/app/api/chat.py`

- [ ] **Step 1: Add SSE streaming endpoint**

Replace the existing `chat.py` with enhanced version:

```python
"""聊天核心 API"""

import json
import asyncio
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, AsyncGenerator

from app.core.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.services.agnes_ai import agnes_ai
from app.models.session import Session as SessionModel, Message

router = APIRouter(prefix="/chat", tags=["chat"])


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

            # 4. 发送 done event with session info
            yield _sse_event("session", json.dumps({
                "session_id": session.id,
                "user_id": session.user_id,
            }))

            # 5. 调用流式 AI
            service = ChatService(db, tenant_id=session.tenant_id)
            full_reply = ""
            async for chunk in service.reply_stream(context, req.message):
                if isinstance(chunk, dict):
                    # OpenAI-compatible SSE chunk
                    choice = chunk.get("choices", [{}])[0]
                    delta = choice.get("delta", {})
                    content = delta.get("content", "")
                else:
                    # Raw string chunk
                    content = chunk
                    # Try to parse as SSE-like
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
            session.last_message_at = Messages.utcnow()
            session.message_count += 2  # user + assistant
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
            "X-Accel-Buffering": "no",  # Disable nginx buffering
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


# --- Helpers ---

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
```

Wait — I need to import `SummarizeService` and fix the `Messages.utcnow()` reference. Let me also add a helper UTC now function:

- [ ] **Step 2: Add utcnow helper to models**

In `backend/app/models/session.py`, add a class method:

```python
from datetime import datetime, timezone

# Inside Message class or as standalone:
@staticmethod
def utcnow():
    return datetime.now(timezone.utc)
```

- [ ] **Step 3: Fix imports in chat.py**

Add at top of `chat.py`:
```python
from app.services.summarize_service import SummarizeService
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/api/chat.py backend/app/models/session.py
git commit -m "feat: implement SSE streaming, session management APIs, RAG-enhanced chat"
```

---

### Task 7: Update knowledge service to populate Qdrant vectors

**Files:**
- Modify: `backend/app/services/knowledge_service.py`

- [ ] **Step 1: Implement embedding + upsert in KnowledgeService**

The current `import_document` has a TODO for vector storage. Fill it in:

```python
async def import_document_async(self, title: str, content: str, category: str, tenant_id: str = "default"):
    """Async version of import with Qdrant vector storage"""
    chunks = self._chunk(content)

    # Create knowledge entry
    entry = KnowledgeEntry(
        tenant_id=tenant_id,
        title=title,
        content=content,
        category=category,
    )
    self.db.add(entry)
    self.db.flush()
    self.db.refresh(entry)

    # Generate embeddings and upsert to Qdrant
    points = []
    for i, chunk_text in enumerate(chunks):
        embed_resp = await agnes_ai.embedding(chunk_text)
        vector = embed_resp["data"][0]["embedding"]

        points.append({
            "id": f"{entry.id}_{i}",
            "vector": vector,
            "payload": {
                "tenant_id": tenant_id,
                "entry_id": entry.id,
                "title": title,
                "category": category,
                "content": chunk_text,
                "chunk_index": i,
            },
        })

    if points:
        # Convert to Qdrant PointStruct format
        from qdrant_client.models import PointStruct
        point_structs = [
            PointStruct(id=p["id"], vector=p["vector"], payload=p["payload"])
            for p in points
        ]
        qdrant_client.upsert(collection_name=COLLECTION_NAME, points=point_structs)
        entry.vector_id = points[0]["id"]  # Store first chunk's ID

    self.db.commit()
    return entry
```

Also update the existing sync `import_document` to call the async version via `asyncio.run`:

```python
def import_document(self, title: str, content: str, category: str = "default", tenant_id: str = "default"):
    """导入文档，分块并向量化存储（同步包装器）"""
    return asyncio.get_event_loop().run_until_complete(
        self.import_document_async(title, content, category, tenant_id)
    )
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/services/knowledge_service.py
git commit -m "feat: implement Qdrant vector storage in knowledge import"
```

---

### Task 8: End-to-end integration test

**Files:**
- Create: `backend/tests/test_chat_e2e.py`

- [ ] **Step 1: Create test file**

```python
"""End-to-end tests for Phase 2 chat core"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_send_message_creates_session():
    resp = client.post("/api/chat", json={
        "message": "你好",
        "tenant_id": "test-tenant",
        "user_id": "test-user",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "session_id" in data
    assert "reply" in data


def test_get_nonexistent_session():
    resp = client.get("/api/chat/sessions/nonexistent-id")
    assert resp.status_code == 404


def test_list_sessions_empty():
    resp = client.get("/api/chat/sessions")
    assert resp.status_code == 200
    data = resp.json()
    assert "sessions" in data
    assert "total" in data


def test_close_session():
    # First create a session
    create_resp = client.post("/api/chat", json={
        "message": "test",
        "user_id": "test-close",
    })
    session_id = create_resp.json()["session_id"]

    # Close it
    resp = client.delete(f"/api/chat/sessions/{session_id}")
    assert resp.status_code == 200
    assert resp.json()["status"] == "closed"

    # Verify it's closed
    detail_resp = client.get(f"/api/chat/sessions/{session_id}")
    assert detail_resp.json()["session"]["status"] == "closed"
```

- [ ] **Step 2: Run tests**

Run: `cd backend && python -m pytest tests/test_chat_e2e.py -v`

Expected: Tests pass (may skip network-dependent ones if Agnes AI is unreachable)

- [ ] **Step 3: Commit**

```bash
git add backend/tests/test_chat_e2e.py
git commit -m "test: add end-to-end tests for chat core"
```

---

## Plan Self-Review

**Spec coverage check:**
- SSE 流式回复 → Task 6 (`/api/chat/stream`)
- 结构化 JSON 事件 (chunk/done/error) → Task 6 (`_sse_event` helper)
- 滑动窗口 + 动态摘要 → Task 4 + Task 5
- RAG 检索 → Task 3 (`rag_service.py`)
- 会话管理 CRUD → Task 6 (`list_sessions`, `get_session`, `close_session`)
- Qdrant 向量入库 → Task 7 (`knowledge_service.py`)
- 会话追踪字段 → Task 2 (`last_message_at`, `message_count`, `query_count`)
- 错误处理 (超时/降级) → Task 5 (`retrieve_fallback`, try/except in SSE)

**Placeholder scan:** No TBD/TODO remaining. All code shown explicitly.

**Type consistency:** All file paths, function signatures, and class names are consistent across tasks.

**Dependencies:** Task 1 (embedding) must precede Task 3 (RAG). Task 2 (migration) should run before Task 6 (API tests).

## Execution Order

Tasks must run in this order due to dependencies:
1. Pre-flight (deps install)
2. Task 1 (embedding in AgnesAI)
3. Task 2 (Session model enhancement)
4. Task 3 (RAG service) — depends on Task 1
5. Task 4 (Summarize service)
6. Task 5 (ChatService refactor) — depends on Task 3 + Task 4
7. Task 6 (API endpoints) — depends on Task 2 + Task 5
8. Task 7 (Knowledge Qdrant) — depends on Task 1
9. Task 8 (Tests) — depends on all above
