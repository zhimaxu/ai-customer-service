# 智能客服系统

基于 Agnes AI 多模态模型的 AI 智能客服 SaaS 平台。

## 快速开始

```bash
# 启动基础设施
docker compose up -d

# 初始化数据库
cd backend && alembic upgrade head

# 启动后端
cd backend && uvicorn app.main:app --reload

# 启动前端
cd frontend && npm run dev
```

## 技术栈

- **前端**: Vue 3 + Vite + Element Plus + ECharts
- **后端**: Python FastAPI + SQLAlchemy + Pydantic
- **数据库**: MySQL 8.0 + Qdrant + Redis
- **AI**: Agnes AI 多模态模型
