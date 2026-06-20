"""RAG (Retrieval-Augmented Generation) service"""

from app.core.qdrant_client import qdrant_client, COLLECTION_NAME
from app.services.agnes_ai import agnes_ai
from qdrant_client.models import Filter, FieldCondition, MatchValue


class RAGService:
    """Knowledge base retrieval service"""

    def __init__(self, tenant_id: str = "default"):
        self.tenant_id = tenant_id

    async def retrieve(self, query: str, top_k: int = 3, score_threshold: float = 0.5) -> list:
        """
        Retrieve relevant knowledge fragments for a query.
        Returns list of text snippets (strings).
        """
        embed_resp = await agnes_ai.embedding(query)
        query_vector = embed_resp["data"][0]["embedding"]

        search_filter = Filter(
            must=[
                FieldCondition(key="tenant_id", match=MatchValue(value=self.tenant_id)),
            ]
        )

        hits = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=top_k,
            score_threshold=score_threshold,
            query_filter=search_filter,
        )

        snippets = []
        for hit in hits:
            snippet = hit.payload.get("content", "")
            if snippet:
                snippets.append(snippet)

        return snippets

    async def retrieve_fallback(self, query: str, top_k: int = 5) -> list:
        """Fallback: search without score threshold"""
        embed_resp = await agnes_ai.embedding(query)
        query_vector = embed_resp["data"][0]["embedding"]

        hits = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=top_k,
            query_filter=Filter(
                must=[
                    FieldCondition(key="tenant_id", match=MatchValue(value=self.tenant_id)),
                ]
            ),
        )

        return [h.payload.get("content", "") for h in hits if h.payload.get("content")]
