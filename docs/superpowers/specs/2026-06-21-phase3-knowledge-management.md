# Phase 3: 知识库管理 — 设计文档

> 日期: 2026-06-21
> 状态: 已审批

---

## 目标

完善知识库管理能力：文件上传转换（PDF/Word/Excel/图片）、知识库搜索、条目 CRUD、Qdrant 自动初始化。

**验收标准**：
- 支持 Markdown/TXT/PDF/Word/Excel 文件上传，自动转为 Markdown 并入库
- 图片上传走 Agnes AI 视觉识别提取文本
- 知识库搜索支持关键词/分类/标签过滤
- 系统启动时自动创建 Qdrant 集合和 payload 索引
- 100 篇文档检索 < 1s

---

## 架构变更

### 新增/修改 API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/knowledge/upload` | 文件上传（multipart/form-data） |
| GET | `/api/knowledge/search` | 知识库搜索（关键词/分类/标签） |
| GET | `/api/knowledge/{id}` | 单个条目详情 |
| PUT | `/api/knowledge/{id}` | 更新条目 |
| POST | `/api/tools/convert` | 文件转 Markdown |

### 核心组件

```
backend/
├── api/
│   └── knowledge.py       ← 增强：upload/search/detail/update
├── services/
│   ├── knowledge_service.py ← 增强：文件转换 + 搜索
│   └── file_converter.py  ← 新增：PDF/Word/Excel/OCR 转换
├── schemas/
│   └── knowledge.py       ← 扩展：SearchRequest, KnowledgeDetailResponse
├── core/
│   └── qdrant_client.py   ← 增强：启动时自动初始化集合
└── main.py                ← 增强：lifespan 初始化
```

---

## 关键技术设计

### 1. 文件转换器 (`file_converter.py`)

**支持的格式及转换策略**：

| 格式 | 库 | 转换方式 |
|------|-----|---------|
| Markdown (.md) | 直读 | 直接返回文本 |
| 纯文本 (.txt) | 直读 | UTF-8 解码 |
| CSV (.csv) | `csv` 模块 | 转为 Markdown 表格 |
| PDF (.pdf) | `pypdf` | 逐页提取文本 |
| Word (.docx) | `python-docx` | 提取段落 + 表格 |
| Excel (.xlsx/.xls) | `openpyxl` | 逐 sheet 提取为 Markdown 表格 |
| 图片 (.png/.jpg/.jpeg/.webp) | Agnes AI `image_recognition` | 视觉模型识别图片内容 |

**file_converter.py 实现**：

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
        return await converters[file_type](file_bytes, filename)

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
        # Convert to Markdown table
        headers = rows[0]
        col_widths = [len(h) for h in headers]
        for row in rows[1:]:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(cell))
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
        return "\n\n".join(pages)

    @staticmethod
    async def _convert_docx(data: bytes, filename: str) -> str:
        from docx import Document
        doc = Document(io.BytesIO(data))
        parts = []
        for element in doc.element.iterchildren():
            tag = element.tag.split("}")[-1] if "}" in element.tag else element.tag
            if tag == "p":
                para_text = ""
                for child in element.iterchildren():
                    if child.tag.endswith("t"):
                        para_text += child.text or ""
                if para_text.strip():
                    parts.append(para_text.strip())
            elif tag == "tbl":
                # Convert table
                table = doc.tables[-1] if doc.tables else None
                if table:
                    for row in table.rows:
                        parts.append(" | ".join(cell.text for cell in row.cells))
        return "\n\n".join(parts)

    @staticmethod
    async def _convert_excel(data: bytes, filename: str) -> str:
        from openpyxl import load_workbook
        wb = load_workbook(io.BytesIO(data), read_only=True)
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
            md_lines = ["| " + " | ".join(str(h).ljust(col_widths[i]) for i, h in enumerate(headers)) + " |"]
            md_lines.append("| " + " | ".join("-" * w for w in col_widths) + " |")
            for row in rows_data[1:]:
                md_lines.append("| " + " | ".join(
                    str(row[i]).ljust(col_widths[i]) if i < len(row) and row[i] is not None else "".ljust(col_widths[0])
                    for i in range(len(headers))
                ) + " |")
            sheets.append(f"## Sheet: {ws_name}\n\n" + "\n".join(md_lines))
        wb.close()
        return "\n\n".join(sheets)

    @staticmethod
    async def _convert_image(data: bytes, filename: str) -> str:
        import base64
        b64 = base64.b64encode(data).decode("utf-8")
        data_url = f"data:image/{Path(filename).suffix.lstrip('.').lower()};base64,{b64}"
        result = await agnes_ai.image_recognition(data_url, "请详细描述这张图片中的所有文字和内容")
        return result["choices"][0]["message"]["content"]
```

### 2. 知识库 API 增强

**文件上传** (`POST /api/knowledge/upload`)：
- 接收 multipart/form-data 文件
- 自动检测文件类型 → 调用 FileConverter 转换
- 转换后走 KnowledgeService.import_document 入库

**知识库搜索** (`GET /api/knowledge/search?q=xxx&category=xxx&tag=xxx`)：
- 从 MySQL 搜索（LIKE 匹配标题/标签）
- 支持分类过滤
- 返回分页结果

**条目详情** (`GET /api/knowledge/{id}`)：
- 返回条目信息 + Qdrant 中的 chunk 列表

**更新条目** (`PUT /api/knowledge/{id}`)：
- 更新标题/内容/分类/标签
- 重新分块 + 重新 embedding

### 3. Qdrant 自动初始化

在 FastAPI lifespan 启动时：
1. 创建 Qdrant 集合（如果不存在）
2. 创建 tenant_id payload 索引

### 4. 依赖

```
pypdf==5.9.0
python-docx==1.2.0
openpyxl==3.1.5
pytesseract==0.3.13
```

---

## 数据流

```
用户上传文件 (.pdf/.docx/.xlsx/.png)
  │
  ▼
FileConverter.detect_type() → 识别格式
  │
  ▼
FileConverter.convert() → 转为 Markdown 文本
  │
  ▼
KnowledgeService.import_document_async()
  ├── 文档分块 (_chunk)
  ├── 逐块 embedding (agnes_ai.embedding)
  └── 批量 upsert 到 Qdrant
  │
  ▼
返回 KnowledgeEntryResponse
```

---

## 错误处理

| 场景 | 处理方式 |
|------|---------|
| 不支持的文件格式 | 返回 400，提示支持的格式列表 |
| PDF 损坏/加密 | 返回 400，显示具体错误 |
| Word 文档含宏 | 跳过宏，只提取文本 |
| 图片识别失败 | 返回 400，提示重试 |
| Qdrant 不可用 | 文档仍存入 MySQL，标记 vectorized=false |
| 空文件 | 返回 400 |

---

## 不包含的内容（Out of Scope）

- 版本控制（知识库条目的变更历史）
- 全文搜索引擎（仅 MySQL LIKE 搜索）
- 图片/视频预览
- 批量导入（ZIP 包解压）
- 权限控制（Phase 1 已有 RBAC 模型但未实现 API）
