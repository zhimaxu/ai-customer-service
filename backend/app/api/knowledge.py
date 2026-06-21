"""知识库 API"""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.schemas.knowledge import (
    KnowledgeEntryCreate,
    KnowledgeEntryResponse,
    KnowledgeDetailResponse,
    KnowledgeUpdateRequest,
)
from app.services.knowledge_service import KnowledgeService
from app.services.file_converter import FileConverter

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.post("/upload", response_model=KnowledgeEntryResponse)
async def upload_knowledge(
    file: UploadFile = File(...),
    title: Optional[str] = None,
    category: str = "default",
    tenant_id: str = "default",
    db: Session = Depends(get_db),
):
    """上传文件到知识库（自动检测格式并转换）"""
    file_type = FileConverter.detect_type(file.filename or "")
    if not file_type:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.filename}. Supported: {', '.join(FileConverter.SUPPORTED_EXTENSIONS.keys())}",
        )

    content_bytes = await file.read()
    if not content_bytes:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        markdown_content = await FileConverter.convert(content_bytes, file.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Conversion failed: {str(e)}")

    if not markdown_content.strip():
        raise HTTPException(status_code=400, detail="Converted content is empty")

    service = KnowledgeService(db)
    entry_title = title or file.filename
    entry = service.import_document(
        title=entry_title,
        content=markdown_content,
        category=category,
        tenant_id=tenant_id,
    )

    return KnowledgeEntryResponse(
        id=entry.id,
        title=entry.title,
        category=entry.category,
        created_at=entry.created_at,
    )


@router.post("", response_model=KnowledgeEntryResponse)
async def create_knowledge(
    req: KnowledgeEntryCreate,
    db: Session = Depends(get_db),
):
    """直接导入 Markdown 文本"""
    service = KnowledgeService(db)
    entry = service.import_document(
        title=req.title,
        content=req.content,
        category=req.category or "default",
    )
    return KnowledgeEntryResponse(
        id=entry.id,
        title=entry.title,
        category=entry.category,
        created_at=entry.created_at,
    )


@router.get("")
async def list_knowledge(
    category: Optional[str] = None,
    tenant_id: str = "default",
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    """获取知识库列表（支持分页和分类过滤）"""
    from app.models.knowledge import KnowledgeEntry
    base = db.query(KnowledgeEntry).filter(KnowledgeEntry.tenant_id == tenant_id)
    if category:
        base = base.filter(KnowledgeEntry.category == category)

    total = base.count()
    entries = (
        base.order_by(KnowledgeEntry.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "entries": [
            {
                "id": e.id,
                "title": e.title,
                "category": e.category,
                "created_at": e.created_at.isoformat(),
            }
            for e in entries
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/search")
async def search_knowledge(
    q: Optional[str] = Query(None, description="Search keyword"),
    category: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    tenant_id: str = "default",
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    """搜索知识库"""
    service = KnowledgeService(db)
    return service.search(query=q, category=category, tag=tag, tenant_id=tenant_id, page=page, page_size=page_size)


@router.get("/{entry_id}", response_model=KnowledgeDetailResponse)
async def get_knowledge(entry_id: str, db: Session = Depends(get_db)):
    """获取知识库条目详情"""
    service = KnowledgeService(db)
    entry = service.get_entry(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Knowledge entry not found")
    return service._entry_to_dict(entry)


@router.put("/{entry_id}", response_model=KnowledgeDetailResponse)
async def update_knowledge(
    entry_id: str,
    req: KnowledgeUpdateRequest,
    db: Session = Depends(get_db),
):
    """更新知识库条目"""
    service = KnowledgeService(db)
    entry = service.update_entry(
        entry_id=entry_id,
        title=req.title,
        content=req.content,
        category=req.category,
        tags=req.tags,
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Knowledge entry not found")
    return service._entry_to_dict(entry)


@router.delete("/{entry_id}")
async def delete_knowledge(entry_id: str, db: Session = Depends(get_db)):
    """删除知识库条目"""
    service = KnowledgeService(db)
    result = service.delete_entry(entry_id)
    return result
