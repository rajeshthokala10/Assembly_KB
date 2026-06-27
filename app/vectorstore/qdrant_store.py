from __future__ import annotations

import logging
from functools import lru_cache

from qdrant_client import QdrantClient, models

from app.config import settings
from app.models.document import ChunkRecord

log = logging.getLogger(__name__)

DENSE_VECTOR_NAME = "dense"
SPARSE_VECTOR_NAME = "bm25"


@lru_cache(maxsize=1)
def get_qdrant_client() -> QdrantClient:
    # Qdrant Cloud: connect via the full https url. Otherwise fall back to
    # host/port for a local or self-hosted instance.
    if settings.qdrant_url:
        kwargs: dict = {"url": settings.qdrant_url}
    else:
        kwargs = {"host": settings.qdrant_host, "port": settings.qdrant_port}
    if settings.qdrant_api_key:
        kwargs["api_key"] = settings.qdrant_api_key
    # Generous timeout so a slow TLS handshake to a distant Cloud region
    # (e.g. sa-east-1) doesn't surface as a 500. Applies to connect + read.
    kwargs["timeout"] = settings.qdrant_timeout
    return QdrantClient(**kwargs)


class QdrantStore:
    def __init__(self) -> None:
        self.client = get_qdrant_client()
        self.collection = settings.qdrant_collection

    def ensure_collection(self) -> None:
        if self.client.collection_exists(self.collection):
            return
        log.info("Creating Qdrant collection: %s", self.collection)
        self.client.create_collection(
            collection_name=self.collection,
            vectors_config={
                DENSE_VECTOR_NAME: models.VectorParams(
                    size=settings.embedding_dim,
                    distance=models.Distance.COSINE,
                ),
            },
            sparse_vectors_config={
                SPARSE_VECTOR_NAME: models.SparseVectorParams(
                    modifier=models.Modifier.IDF,
                ),
            },
        )
        self._create_payload_indices()

    def _create_payload_indices(self) -> None:
        for field in ("state", "language", "category", "security_level", "chunk_type", "document_id"):
            self.client.create_payload_index(
                collection_name=self.collection,
                field_name=field,
                field_schema=models.PayloadSchemaType.KEYWORD,
            )
        for field in ("allowed_roles", "allowed_states"):
            self.client.create_payload_index(
                collection_name=self.collection,
                field_name=field,
                field_schema=models.PayloadSchemaType.KEYWORD,
            )

    async def upsert_chunks(
        self,
        chunks: list[ChunkRecord],
        dense_vectors: list[list[float]],
        sparse_vectors: list[tuple[list[int], list[float]]],
    ) -> None:
        self.ensure_collection()
        points: list[models.PointStruct] = []

        for chunk, dense_vec, (sp_indices, sp_values) in zip(chunks, dense_vectors, sparse_vectors):
            payload = chunk.model_dump(exclude={"text"})
            payload["text"] = chunk.text

            vectors: dict = {DENSE_VECTOR_NAME: dense_vec}
            if sp_indices:
                vectors[SPARSE_VECTOR_NAME] = models.SparseVector(indices=sp_indices, values=sp_values)

            points.append(models.PointStruct(id=_deterministic_id(chunk.chunk_id), vector=vectors, payload=payload))

        batch_size = 100
        for i in range(0, len(points), batch_size):
            self.client.upsert(collection_name=self.collection, points=points[i : i + batch_size])

    def hybrid_search(
        self,
        dense_vector: list[float],
        sparse_indices: list[int],
        sparse_values: list[float],
        *,
        limit: int = 20,
        candidate_multiplier: int = 4,
        query_filter: models.Filter | None = None,
    ) -> list[models.ScoredPoint]:
        """Single-request hybrid search with server-side Reciprocal Rank Fusion.

        Qdrant prefetches the dense and sparse candidate lists and fuses them
        with RRF inside the engine — one round trip instead of two queries plus
        client-side fusion. The RBAC filter is applied to *both* prefetches so
        nothing unpermitted ever enters the candidate pool.
        """
        candidate_limit = limit * candidate_multiplier
        prefetch: list[models.Prefetch] = [
            models.Prefetch(
                query=dense_vector,
                using=DENSE_VECTOR_NAME,
                limit=candidate_limit,
                filter=query_filter,
            )
        ]
        if sparse_indices:
            prefetch.append(
                models.Prefetch(
                    query=models.SparseVector(indices=sparse_indices, values=sparse_values),
                    using=SPARSE_VECTOR_NAME,
                    limit=candidate_limit,
                    filter=query_filter,
                )
            )

        return self.client.query_points(
            collection_name=self.collection,
            prefetch=prefetch,
            query=models.FusionQuery(fusion=models.Fusion.RRF),
            limit=limit,
            query_filter=query_filter,
            with_payload=True,
        ).points

    def retrieve_texts_by_chunk_ids(self, chunk_ids: list[str]) -> dict[str, str]:
        """Batch-fetch chunk text by chunk_id in a SINGLE request.

        Points are stored under a deterministic id derived from chunk_id, so we
        can retrieve directly by point id (no per-chunk scroll query). Returns a
        ``{chunk_id: text}`` map for the ids that exist.
        """
        ids = list(dict.fromkeys(cid for cid in chunk_ids if cid))
        if not ids:
            return {}
        records = self.client.retrieve(
            collection_name=self.collection,
            ids=[_deterministic_id(cid) for cid in ids],
            with_payload=True,
        )
        out: dict[str, str] = {}
        for rec in records:
            payload = rec.payload or {}
            cid = payload.get("chunk_id")
            if cid:
                out[cid] = payload.get("text", "")
        return out

    def search_dense(
        self, vector: list[float], *, limit: int = 20, query_filter: models.Filter | None = None,
    ) -> list[models.ScoredPoint]:
        return self.client.query_points(
            collection_name=self.collection,
            query=vector,
            using=DENSE_VECTOR_NAME,
            limit=limit,
            query_filter=query_filter,
            with_payload=True,
        ).points

    def search_sparse(
        self, indices: list[int], values: list[float], *, limit: int = 20, query_filter: models.Filter | None = None,
    ) -> list[models.ScoredPoint]:
        return self.client.query_points(
            collection_name=self.collection,
            query=models.SparseVector(indices=indices, values=values),
            using=SPARSE_VECTOR_NAME,
            limit=limit,
            query_filter=query_filter,
            with_payload=True,
        ).points

    def get_by_chunk_id(self, chunk_id: str) -> models.Record | None:
        """Fetch a single record by chunk_id.

        Points are stored under a deterministic id derived from chunk_id, so we
        retrieve directly by point id. This avoids filtering on the unindexed
        ``chunk_id`` payload field (which Qdrant rejects with a 400).
        """
        if not chunk_id:
            return None
        records = self.client.retrieve(
            collection_name=self.collection,
            ids=[_deterministic_id(chunk_id)],
            with_payload=True,
        )
        return records[0] if records else None


def _deterministic_id(chunk_id: str) -> str:
    import hashlib
    return hashlib.md5(chunk_id.encode()).hexdigest()
