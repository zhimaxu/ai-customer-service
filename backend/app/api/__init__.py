"""API 路由挂载"""

from fastapi import APIRouter

from app.api.chat import router as chat_router
from app.api.knowledge import router as knowledge_router
from app.api.agent import router as agent_router
from app.api.admin import router as admin_router
from app.api.system import router as system_router
from app.api.ticket import router as ticket_router
from app.api.ws import router as ws_router
from app.api.stats import router as stats_router

api_router = APIRouter()
api_router.include_router(chat_router)
api_router.include_router(knowledge_router)
api_router.include_router(agent_router)
api_router.include_router(admin_router)
api_router.include_router(system_router)
api_router.include_router(ticket_router)
api_router.include_router(ws_router)
api_router.include_router(stats_router)
