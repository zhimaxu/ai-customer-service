"""后台管理 API"""

from fastapi import APIRouter

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/login")
def admin_login():
    """管理员登录（占位）"""
    return {"message": "Login endpoint - coming soon"}


@router.get("/me")
def get_current_admin():
    """获取当前管理员信息（占位）"""
    return {"message": "Profile endpoint - coming soon"}
