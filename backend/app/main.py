"""FastAPI 应用入口"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import api_router
from app.core.qdrant_client import init_collection, init_payload_schema, qdrant_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup: initialize Qdrant collection"""
    init_collection(qdrant_client)
    init_payload_schema(qdrant_client)
    yield
    # Shutdown cleanup (if any)


app = FastAPI(
    title=settings.APP_NAME,
    version="0.2.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载路由
app.include_router(api_router, prefix="/api")


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "version": "0.2.0"}
