"""知识库服务"""

import re
from sqlalchemy.orm import Session
from app.core.qdrant_client import qdrant_client, COLLECTION_NAME, VECTOR_SIZE
from app.models.knowledge import KnowledgeEntry
from app.services.agnes_ai import agnes_ai


class KnowledgeService:
    """知识库服务"""

    def __init__(self, db: Session):
        self.db = db

    def import_document(self, title: str, content: str, category: str = "default"):
        """导入文档，分块并向量化存储"""
        chunks = self._chunk(content)

        # 创建知识库条目
        entry = KnowledgeEntry(title=title, content=content, category=category)
        self.db.add(entry)
        self.db.flush()

        # TODO: 调用 Agnes embedding API 生成向量并存入 Qdrant
        # for chunk in chunks:
        #     vector = await agnes_ai.embedding(chunk.text)
        #     qdrant_client.upsert(COLLECTION_NAME, points=[PointStruct(...)])

        self.db.commit()
        self.db.refresh(entry)
        return entry

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
