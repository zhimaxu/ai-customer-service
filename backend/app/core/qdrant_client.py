"""Qdrant 向量数据库客户端"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from app.core.config import settings

COLLECTION_NAME = "knowledge_vectors"
VECTOR_SIZE = 768  # Agnes embedding 向量维度


def get_qdrant_client() -> QdrantClient:
    """获取 Qdrant 客户端"""
    return QdrantClient(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT,
    )


def init_collection(client: QdrantClient):
    """初始化向量集合"""
    collections = client.get_collections().collections
    if not any(c.name == COLLECTION_NAME for c in collections):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )


qdrant_client = get_qdrant_client()
