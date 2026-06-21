# Phase 3: 知识库管理 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete knowledge base management: file upload/conversion (PDF/Word/Excel/Markdown), knowledge search, Qdrant auto-init, and enhanced CRUD APIs.

**Architecture:** Add a dedicated FileConverter service supporting 7+ formats, enhance the knowledge API with upload/search/detail/update endpoints, and wire Qdrant collection initialization into FastAPI lifespan.

**Tech Stack:** FastAPI, pypdf, python-docx, openpyxl, Agnes AI (image recognition), Qdrant

---

### Pre-flight: Install dependencies

**Files:**
- Modify: `backend/requirements.txt`

- [ ] **Step 1: Add file conversion dependencies**

Append these to `backend/requirements.txt`:

```
# File conversion
pypdf==5.9.0
python-docx==1.2.0
openpyxl==3.1.5
```

- [ ] **Step 2: Install**

Run: `cd backend && pip install pypdf==5.9.0 python-docx==1.2.0 openpyxl==3.1.5`

Expected: All 3 packages install successfully

- [ ] **Step 3: Commit**

```bash
git add backend/requirements.txt
git commit -m "chore: add file conversion dependencies for Phase 3"
```

---

### Task 1: Create FileConverter service

**Files:**
- Create: `backend/app/services/file_converter.py`

- [ ] **Step 1: Create file_converter.py**

```python
"""文件转换服务 — 将各种格式转为 Markdown"""

import csv
import io
from pathlib import Path
from typing import Optional

from app.services.agnes_ai import agnes_ai


class FileConverter:
    """文件到 Markdown 的转换器"""

    SUPPORTED_EXTENSIONS = {
        ".md": "markdown",
        ".txt": "text",
        ".csv": "csv",
        ".pdf": "pdf",
        ".docx": "docx",
        ".xlsx": "excel",
        ".xls": "excel",
        ".png": "image",
        ".jpg": "image",
        ".jpeg": "image",
        ".webp": "image",
    }

    @classmethod
    def detect_type(cls, filename: str) -> Optional[str]:
        ext = Path(filename).suffix.lower()
        return cls.SUPPORTED_EXTENSIONS.get(ext)

    @classmethod
    async def convert(cls, file_bytes: bytes, filename: str) -> str:
        file_type = cls.detect_type(filename)
        if not file_type:
            raise ValueError(f"Unsupported file type: {filename}")

        converters = {
            "markdown": cls._convert_markdown,
            "text": cls._convert_text,
            "csv": cls._convert_csv,
            "pdf": cls._convert_pdf,
            "docx": cls._convert_docx,
            "excel": cls._convert_excel,
            "image": cls._convert_image,
        }
        converter = converters[file_type]
        # Sync converters don't need await, async ones do
        if file_type in ("markdown", "text", "csv"):
            return converter(file_bytes, filename)
        return await converter(file_bytes, filename)

    @staticmethod
    def _convert_markdown(data: bytes, filename: str) -> str:
        return data.decode("utf-8", errors="replace")

    @staticmethod
    def _convert_text(data: bytes, filename: str) -> str:
        return data.decode("utf-8", errors="replace")

    @staticmethod
    def _convert_csv(data: bytes, filename: str) -> str:
        text = data.decode("utf-8", errors="replace")
        reader = csv.reader(io.StringIO(text))
        rows = list(reader)
        if not rows:
            return ""
        headers = rows[0]
        col_widths = [len(h) for h in headers]
        for row in rows[1:]:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))
        md_lines = ["| " + " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers)) + " |"]
        md_lines.append("| " + " | ".join("-" * w for w in col_widths) + " |")
        for row in rows[1:]:
            md_lines.append("| " + " | ".join(
                str(row[i]).ljust(col_widths[i]) if i < len(row) else "".ljust(col_widths[0])
                for i in range(len(headers))
            ) + " |")
        return "\n".join(md_lines)

    @staticmethod
    async def _convert_pdf(data: bytes, filename: str) -> str:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(data))
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        return "\n\n".join(pages) if pages else ""

    @staticmethod
    async def _convert_docx(data: bytes, filename: str) -> str:
        from docx import Document
        doc = Document(io.BytesIO(data))
        parts = []
        for para in doc.paragraphs:
            if para.text.strip():
                parts.append(para.text.strip())
        for table in doc.tables:
            for row in table.rows:
                parts.append(" | ".join(cell.text for cell in row.cells))
        return "\n\n".join(parts)

    @staticmethod
    async def _convert_excel(data: bytes, filename: str) -> str:
        from openpyxl import load_workbook
        wb = load_workbook(io.BytesIO(data), read_only=True, data_only=True)
        sheets = []
        for ws_name in wb.sheetnames:
            ws = wb[ws_name]
            rows_data = list(ws.values)
            if not rows_data:
                continue
            headers = rows_data[0]
            col_widths = [len(str(h)) for h in headers]
            for row in rows_data[1:]:
                for i, cell in enumerate(row):
                    if cell is not None:
                        col_widths[i] = max(col_widths[i], len(str(cell)))
            md_lines = ["## Sheet: " + ws_name, ""]
            md_lines.append("| " + " | ".join(str(h).ljust(col_widths[i]) for i, h in enumerate(headers)) + " |")
            md_lines.append("| " + " | ".join("-" * w for w in col_widths) + " |")
            for row in rows_data[1:]:
                md_lines.append("| " + " | ".join(
                    str(row[i]).ljust(col_widths[i]) if i < len(row) and row[i] is not None else "".ljust(col_widths[0])
                    for i in range(len(headers))
                ) + " |")
            sheets.append("\n".join(md_lines))
        wb.close()
        return "\n\n".join(sheets)

    @staticmethod
    async def _convert_image(data: bytes, filename: str) -> str:
        import base64
        suffix = Path(filename).suffix.lstrip(".").lower()
        b64 = base64.b64encode(data).decode("utf-8")
        data_url = f"data:image/{suffix};base64,{b64}"
        result = await agnes_ai.image_recognition(
            data_url,
            "请详细描述这张图片中的所有文字和内容，保留原始格式"
        )
        return result["choices"][0]["message"]["content"]
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/services/file_converter.py
git commit -m "feat: add FileConverter service for PDF/Word/Excel/CSV/image conversion"
```

---

### Task 2: Enhance KnowledgeService with search + update

**Files:**
- Modify: `backend/app/services/knowledge_service.py`

- [ ] **Step 1: Add search and update methods**

Add these methods to the existing `KnowledgeService` class:

```python
    def search(self, query: str = None, category: str = None, tag: str = None,
               tenant_id: str = "default", page: int = 1, page_size: int = 20) -> dict:
        """Search knowledge entries by keyword/category/tag"""
        base_query = self.db.query(KnowledgeEntry).filter(
            KnowledgeEntry.tenant_id == tenant_id
        )

        if query:
            base_query = base_query.filter(
                sa.or_(
                    KnowledgeEntry.title.contains(query),
                    KnowledgeEntry.content.contains(query),
                    KnowledgeEntry.tags.contains(query),
                )
            )
        if category:
            base_query = base_query.filter(KnowledgeEntry.category == category)
        if tag:
            base_query = base_query.filter(KnowledgeEntry.tags.like(f"%{tag}%"))

        total = base_query.count()
        entries = (
            base_query.order_by(KnowledgeEntry.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return {
            "entries": [self._entry_to_dict(e) for e in entries],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def get_entry(self, entry_id: str) -> Optional[KnowledgeEntry]:
        """Get single knowledge entry"""
        return self.db.query(KnowledgeEntry).filter(KnowledgeEntry.id == entry_id).first()

    def update_entry(self, entry_id: str, title: str = None, content: str = None,
                     category: str = None, tags: str = None, tenant_id: str = "default") -> Optional[KnowledgeEntry]:
        """Update a knowledge entry"""
        entry = self.db.query(KnowledgeEntry).filter(
            sa.and_(KnowledgeEntry.id == entry_id, KnowledgeEntry.tenant_id == tenant_id)
        ).first()
        if not entry:
            return None
        if title:
            entry.title = title
        if content:
            entry.content = content
        if category:
            entry.category = category
        if tags:
            entry.tags = tags
        self.db.commit()
        self.db.refresh(entry)
        return entry

    @staticmethod
    def _entry_to_dict(entry) -> dict:
        return {
            "id": entry.id,
            "tenant_id": entry.tenant_id,
            "title": entry.title,
            "category": entry.category,
            "tags": entry.tags,
            "vector_id": entry.vector_id,
            "created_at": entry.created_at.isoformat() if entry.created_at else None,
            "updated_at": entry.updated_at.isoformat() if entry.updated_at else None,
        }
```

Also add `import sqlalchemy as sa` at the top of the file.

- [ ] **Step 2: Commit**

```bash
git add backend/app/services/knowledge_service.py
git commit -m "feat: add search, update, and detail methods to KnowledgeService"
```

---

### Task 3: Enhance Knowledge API endpoints

**Files:**
- Modify: `backend/app/api/knowledge.py`
- Modify: `backend/app/schemas/knowledge.py`

- [ ] **Step 1: Expand schemas**

Add to `backend/app/schemas/knowledge.py`:

```python
class KnowledgeSearchRequest(BaseModel):
    q: Optional[str] = None
    category: Optional[str] = None
    tag: Optional[str] = None
    page: int = 1
    page_size: int = 20


class KnowledgeUpdateRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None


class KnowledgeDetailResponse(KnowledgeEntryResponse):
    tenant_id: str
    tags: Optional[str]
    vector_id: Optional[str]
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)
```

- [ ] **Step 2: Rewrite knowledge.py API**

Replace `backend/app/api/knowledge.py` with:

```python
"""知识库 API"""

import asyncio
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
from app.core.qdrant_client import qdrant_client, COLLECTION_NAME
from qdrant_client.models import PointStruct

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
    # Detect file type
    file_type = FileConverter.detect_type(file.filename or "")
    if not file_type:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.filename}. Supported: {', '.join(FileConverter.SUPPORTED_EXTENSIONS.keys())}",
        )

    # Read file content
    content_bytes = await file.read()
    if not content_bytes:
        raise HTTPException(status_code=400, detail="Empty file")

    # Convert to Markdown
    try:
        markdown_content = await FileConverter.convert(content_bytes, file.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Conversion failed: {str(e)}")

    if not markdown_content.strip():
        raise HTTPException(status_code=400, detail="Converted content is empty")

    # Import into knowledge base
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
    service = KnowledgeService(db)
    query = db.query(KnowledgeService.__class__.__bases__[0].__new__(KnowledgeService))
    # Simpler approach: direct query
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
    return service.delete_entry(entry_id)
```

Wait — the `list_knowledge` endpoint has a weird `KnowledgeService.__class__.__bases__` hack. Let me simplify it:

Replace the `list_knowledge` function body with:

```python
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
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/api/knowledge.py backend/app/schemas/knowledge.py
git commit -m "feat: enhance knowledge API with upload, search, detail, update endpoints"
```

---

### Task 4: Wire Qdrant auto-init into FastAPI lifespan

**Files:**
- Modify: `backend/app/main.py`
- Modify: `backend/app/core/qdrant_client.py`

- [ ] **Step 1: Add lifespan to main.py**

Replace `backend/app/main.py` with:

```python
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
    # Initialize Qdrant collection and indexes
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
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/main.py backend/app/core/qdrant_client.py
git commit -m "feat: add Qdrant auto-initialization via FastAPI lifespan"
```

---

### Task 5: Add knowledge tests

**Files:**
- Create: `backend/tests/test_knowledge.py`

- [ ] **Step 1: Create test file**

```python
"""Tests for Phase 3 knowledge management"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["version"] == "0.2.0"


def test_list_knowledge_empty():
    resp = client.get("/api/knowledge")
    assert resp.status_code == 200
    data = resp.json()
    assert "entries" in data
    assert data["total"] == 0


def test_search_knowledge_empty():
    resp = client.get("/api/knowledge/search?q=test")
    assert resp.status_code == 200
    data = resp.json()
    assert "entries" in data


def test_get_nonexistent_knowledge():
    resp = client.get("/api/knowledge/nonexistent-id")
    assert resp.status_code == 404


def test_detect_supported_file_types():
    from app.services.file_converter import FileConverter
    for ext in [".md", ".txt", ".csv", ".pdf", ".docx", ".xlsx", ".png", ".jpg"]:
        assert FileConverter.detect_type(f"file{ext}") is not None
    assert FileConverter.detect_type("file.xyz") is None


def test_convert_plain_text():
    from app.services.file_converter import FileConverter
    import asyncio
    result = asyncio.get_event_loop().run_until_complete(
        FileConverter.convert(b"Hello world", "test.txt")
    )
    assert result == "Hello world"


def test_convert_markdown():
    from app.services.file_converter import FileConverter
    import asyncio
    content = "# Title\n\nParagraph 1\n\nParagraph 2"
    result = asyncio.get_event_loop().run_until_complete(
        FileConverter.convert(content.encode(), "test.md")
    )
    assert result == content


def test_convert_csv_to_table():
    from app.services.file_converter import FileConverter
    import asyncio
    csv_content = "Name,Age,City\nAlice,30,Beijing\nBob,25,Shanghai"
    result = asyncio.get_event_loop().run_until_complete(
        FileConverter.convert(csv_content.encode(), "test.csv")
    )
    assert "Name" in result
    assert "Alice" in result
    assert "|" in result  # Markdown table format
```

- [ ] **Step 2: Run tests**

Run: `cd backend && python -m pytest tests/test_knowledge.py -v`

Expected: All tests pass (network-independent ones)

- [ ] **Step 3: Commit**

```bash
git add backend/tests/test_knowledge.py
git commit -m "test: add knowledge management tests"
```

---

## Execution Order

Tasks must run in this order due to dependencies:
1. Pre-flight (deps install)
2. Task 1 (FileConverter) — independent
3. Task 2 (KnowledgeService search/update) — depends on existing KnowledgeService
4. Task 3 (Knowledge API) — depends on Task 1 + Task 2
5. Task 4 (Qdrant auto-init) — independent
6. Task 5 (Tests) — depends on all above

## Plan Self-Review

**Spec coverage:**
- 文件转换（PDF/Word/Excel/CSV/图片/Markdown/TXT）→ Task 1
- 知识库搜索（关键词/分类/标签）→ Task 2 + Task 3
- 条目 CRUD（详情/更新/删除）→ Task 2 + Task 3
- 文件上传 API（multipart/form-data）→ Task 3
- Qdrant 自动初始化 → Task 4
- 依赖安装 → Pre-flight

**Placeholder scan:** All code shown explicitly. No TBD/TODO.

**Type consistency:** All imports, class names, and method signatures match across tasks.

**Edge cases handled:** Empty files, unsupported formats, corrupted PDFs, empty conversion results all addressed in the design doc and reflected in error handling in the API.
