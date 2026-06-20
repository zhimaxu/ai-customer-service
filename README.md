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


## 注意事项
- 检查docker镜像站是否正常
'''ps
完全重建（无缓存，重新创建）的主要命令是 docker-compose up -d --force-recreate --build。
如果只是更改了卷或环境变量，而无需重建镜像，则为 docker-compose up -d --force-recreate。
如果还需要拉取新镜像，则为 docker-compose up -d --force-recreate --pull always。
'''