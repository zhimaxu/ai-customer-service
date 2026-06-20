"""系统配置 API"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db

router = APIRouter(prefix="/system/config", tags=["system"])


@router.get("")
def get_config(key: str = None, db: Session = Depends(get_db)):
    """获取系统配置"""
    from app.models.system_config import SystemConfig

    if key:
        cfg = db.query(SystemConfig).filter(SystemConfig.key == key).first()
        return {"key": cfg.key, "value": cfg.value} if cfg else {}
    configs = db.query(SystemConfig).all()
    return [{"key": c.key, "value": c.value} for c in configs]


@router.put("/{key}")
def update_config(key: str, value: str, db: Session = Depends(get_db)):
    """更新配置项"""
    from app.models.system_config import SystemConfig

    cfg = db.query(SystemConfig).filter(SystemConfig.key == key).first()
    if cfg:
        cfg.value = value
    else:
        cfg = SystemConfig(key=key, value=value)
        db.add(cfg)
    db.commit()
    return {"status": "updated"}
