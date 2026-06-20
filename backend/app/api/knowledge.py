"""知识库 API"""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.knowledge import KnowledgeEntryCreate, KnowledgeEntryResponse
from app.services.knowledge_service import KnowledgeService

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.post("", response_model=KnowledgeEntryResponse)
async def upload_knowledge(
    file: UploadFile = File(None),
    data: str = None,
    title: str = None,
    category: str = "default",
    db: Session = Depends(get_db),
):
    """导入知识库（Markdown 文本或文件）"""
    content = data
    if file:
        content = await file.read()
        if isinstance(content, bytes):
            content = content.decode("utf-8")

    if not content:
        raise HTTPException(status_code=400, detail="No content provided")

    service = KnowledgeService(db)
    entry = service.import_document(title or "Untitled", content, category)
    return KnowledgeEntryResponse(
        id=entry.id,
        title=entry.title,
        category=entry.category,
        created_at=entry.created_at,
    )


@router.get("")
async def list_knowledge(db: Session = Depends(get_db)):
    """获取知识库列表"""
    service = KnowledgeService(db)
    return service.list_entries()


@router.delete("/{entry_id}")
async def delete_knowledge(entry_id: str, db: Session = Depends(get_db)):
    """删除知识库条目"""
    service = KnowledgeService(db)
    return service.delete_entry(entry_id)
