"""工单管理 API"""

from fastapi import APIRouter

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("")
def list_tickets():
    """获取工单列表（占位）"""
    return {"message": "Ticket list - coming soon"}


@router.post("")
def create_ticket():
    """创建工单（占位）"""
    return {"message": "Create ticket - coming soon"}
