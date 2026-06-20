"""知识库服务"""

import asyncio
import re
from sqlalchemy.orm import Session
from app.core.qdrant_client import qdrant_client, COLLECTION_NAME, VECTOR_SIZE
from app.models.knowledge import KnowledgeEntry
from app.services.agnes_ai import agnes_ai


class KnowledgeService:
    """知识库服务"""

    def __init__(self, db: Session):
        self.db = db

    async def import_document_async(self, title: str, content: str, category: str, tenant_id: str = "default"):
        """Async version of import with Qdrant vector storage"""
        from qdrant_client.models import PointStruct

        chunks = self._chunk(content)

        # Create knowledge entry
        entry = KnowledgeEntry(
            tenant_id=tenant_id,
            title=title,
            content=content,
            category=category,
        )
        self.db.add(entry)
        self.db.flush()
        self.db.refresh(entry)

        # Generate embeddings and upsert to Qdrant
        points = []
        for i, chunk_text in enumerate(chunks):
            embed_resp = await agnes_ai.embedding(chunk_text)
            vector = embed_resp["data"][0]["embedding"]

            points.append({
                "id": f"{entry.id}_{i}",
                "vector": vector,
                "payload": {
                    "tenant_id": tenant_id,
                    "entry_id": entry.id,
                    "title": title,
                    "category": category,
                    "content": chunk_text,
                    "chunk_index": i,
                },
            })

        if points:
            point_structs = [
                PointStruct(id=p["id"], vector=p["vector"], payload=p["payload"])
                for p in points
            ]
            qdrant_client.upsert(collection_name=COLLECTION_NAME, points=point_structs)
            entry.vector_id = points[0]["id"]

        self.db.commit()
        return entry

    def import_document(self, title: str, content: str, category: str = "default", tenant_id: str = "default"):
        """导入文档，分块并向量化存储（同步包装器）"""
        return asyncio.get_event_loop().run_until_complete(
            self.import_document_async(title, content, category, tenant_id)
        )

    def _chunk(self, text: str, chunk_size: int = 500, overlap: int = 50) -> list:
        """文档分块"""
        paragraphs = re.split(r'\n\s*\n', text.strip())
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            if len(current_chunk) + len(para) > chunk_size:
                chunks.append(current_chunk.strip())
                current_chunk = current_chunk[-overlap:] + para if overlap else para
            else:
                current_chunk += "\n\n" + para if current_chunk else para

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def list_entries(self) -> list:
        """获取知识库条目列表"""
        return self.db.query(KnowledgeEntry).order_by(KnowledgeEntry.created_at.desc()).all()

    def delete_entry(self, entry_id: str) -> dict:
        """删除知识库条目"""
        entry = self.db.query(KnowledgeEntry).filter(KnowledgeEntry.id == entry_id).first()
        if not entry:
            return {"error": "Not found"}
        self.db.delete(entry)
        self.db.commit()
        return {"status": "deleted"}
