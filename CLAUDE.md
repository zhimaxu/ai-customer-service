# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-powered customer service SaaS platform based on Agnes AI multimodal models. Vue 3 + FastAPI frontend-backend separation architecture supporting multi-tenant deployment, multi-channel access, and ticket workflow.

## Quick Start

```bash
# Start infrastructure (MySQL, Qdrant, Redis, RabbitMQ)
docker compose up -d

# Initialize database
cd backend && alembic upgrade head

# Start backend (port 8000, auto-reload)
cd backend && uvicorn app.main:app --reload

# Start frontend (port 5173, proxies /api to backend)
cd frontend && npm run dev
```

## Development Commands

| Task | Command |
|------|---------|
| Backend dev server | `cd backend && uvicorn app.main:app --reload` |
| Frontend dev server | `cd frontend && npm run dev` |
| Frontend build | `cd frontend && npm run build` |
| Frontend preview | `cd frontend && npm run preview` |
| Database migrations | `cd backend && alembic revision --autogenerate -m "description"` |
| Apply migrations | `cd backend && alembic upgrade head` |
| Run tests | `cd backend && pytest` |
| Health check | `curl http://localhost:8000/api/health` |
| API docs | Open `http://localhost:8000/api/docs` |

## Architecture

### Backend (FastAPI)

```
backend/app/
  main.py              # App entry, lifespan, CORS, router mounting
  api/                 # All REST endpoints (route modules)
    __init__.py        # Mounts all routers under /api prefix
    chat.py            # POST /chat, /chat/stream, session CRUD
    knowledge.py       # Document import, search, CRUD
    agent.py           # Customer service workspace (takeover, reply, quick-reply)
    admin.py           # Admin login, RBAC
    system.py          # System configuration
    ticket.py          # Ticket CRUD
    ws.py              # WebSocket endpoint
    stats.py           # Analytics endpoints
  services/            # Business logic layer
    chat_service.py    # Core chat: RAG + sliding window + summarization
    knowledge_service.py # Doc chunking, embedding, Qdrant upsert
    rag_service.py     # Vector similarity search against knowledge base
    agnes_ai.py        # Agnes AI client (chat, embedding, image, video, vision)
    ws_service.py      # WebSocket connection manager
    summarize_service.py # Conversation summarization (sliding window)
    file_converter.py  # File-to-Markdown converter (PDF, DOCX, CSV, etc.)
  models/              # SQLAlchemy ORM models
    session.py         # Session, Message, Satisfaction
    knowledge.py       # KnowledgeEntry
    analytics.py       # RatingRecord, AgentEfficiencyLog
    tenant.py          # Tenant, TenantPlan
    rbac.py            # User, Role, Permission
    ticket.py          # Ticket
    system_config.py   # SystemConfig
  schemas/             # Pydantic request/response models
  core/                # Infrastructure
    config.py          # Pydantic Settings (env vars)
    database.py        # SQLAlchemy engine, session, Base
    qdrant_client.py   # Qdrant singleton, collection init
```

Key patterns:
- All API routers mount under `/api` prefix via `api/__init__.py`
- Services are pure business logic, called by API handlers
- `get_db()` dependency injection for SQLAlchemy sessions
- AgnesAI is a singleton wrapping the Agnes AI API (OpenAI-compatible)
- RAG pipeline: user query → embedding → Qdrant vector search → context injection → LLM generation

### Frontend (Vue 3)

```
frontend/src/
  main.js              # App entry, Pinia, Element Plus setup
  App.vue              # Root component
  router/index.js      # Routes: /login, /, /dashboard, /agent (+ auth guard)
  api/request.js       # Axios instance with JWT interceptor
  stores/
    auth.js            # Login state, token management (localStorage)
    session.js         # Chat session state
    agent.js           # Customer workspace state
  views/
    Login.vue          # Login form
    ChatView.vue       # Customer-facing chat (Phase 4)
    AgentView.vue      # Customer service workspace (Phase 5)
    DashboardView.vue  # Analytics dashboard (Phase 6)
  components/
    ChatWindow.vue     # Message display + input area
    SessionList.vue    # Session sidebar
    MessageBubble.vue  # User message bubble
    AgentMessageBubble.vue  # Agent-style message bubble
    TypingIndicator.vue # "typing..." animation
    FileUpload.vue     # File upload component
    AgentSidebar.vue   # Workspace sidebar with session tabs
    AgentChat.vue      # Full agent chat view
    SettingsPanel.vue  # Configuration panel
```

Key patterns:
- Pinia stores for state management (auth, session, agent)
- Axios interceptors handle JWT token injection and 401 redirects
- Vite proxies `/api` to `localhost:8000` in dev mode
- SSE (Server-Sent Events) for streaming AI responses
- WebSocket for real-time customer service notifications

### Data Flow

```
Customer chat:    Frontend → POST /api/chat/stream (SSE) → ChatService → AgnesAI + RAG → Qdrant
Agent workspace:  Frontend → WebSocket → ConnectionManager → Real-time session updates
Knowledge:        Frontend → POST /api/knowledge → chunk → embedding → Qdrant upsert
Analytics:        Frontend → GET /api/stats/* → SQLAlchemy aggregations → ECharts
```

## Key Technical Details

- **AI Model**: Agnes AI (agnes-2.0-flash for text, agnes-embedding-v1 for vectors). API is OpenAI-compatible.
- **Vector DB**: Qdrant collection `knowledge_vectors`, 768-dim cosine similarity, filtered by `tenant_id` payload.
- **RAG**: Embed user query → search Qdrant → inject top-k snippets as system context → call LLM.
- **Context Management**: Sliding window (last 20 messages) + summarization of older messages (threshold: 40 messages).
- **Multi-tenant**: `tenant_id` on all business models, Qdrant payload filters by tenant.
- **Auth**: JWT stored in localStorage, axios interceptor adds Bearer token.
- **DB**: MySQL 8.0, SQLAlchemy ORM, Alembic migrations. All tables use UUID primary keys.
- **Path convention**: Always use forward slashes `/` in code paths (Windows compatible).

## Running Tests

```bash
cd backend
pytest                              # Run all tests
pytest tests/test_chat_e2e.py       # Chat module tests
pytest tests/test_knowledge.py      # Knowledge module tests
```

Tests use `fastapi.testclient.TestClient` for synchronous HTTP testing. They cover session CRUD, knowledge search, and file conversion. AI-dependent endpoints accept 200 or 5xx (service unavailable).

## Docker Infrastructure

Services defined in `docker-compose.yml`:
- `mysql` (3306) — MySQL 8.4 with utf8mb4
- `qdrant` (6333/6334) — Vector search
- `redis` (6379) — Cache/session storage
- `rabbitmq` (5672/15672) — Message queue + management UI
- `backend` (8000) — FastAPI app
- `frontend` (80) — Nginx-serving Vue SPA

Rebuild all: `docker compose up -d --force-recreate --build`
