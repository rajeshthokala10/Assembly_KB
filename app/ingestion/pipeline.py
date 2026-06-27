from __future__ import annotations

import logging
import uuid
from pathlib import Path

from app.ingestion.chunker import HierarchicalChunker
from app.ingestion.embeddings import DenseEncoder, SparseBM25Encoder
from app.ingestion.ocr_engine import OCREngine
from app.models.document import ChunkRecord, DocumentCategory, DocumentMetadata, IngestRequest, IngestResponse
from app.vectorstore.qdrant_store import QdrantStore

log = logging.getLogger(__name__)


class IngestionPipeline:
    def __init__(self) -> None:
        self.ocr = OCREngine()
        self.chunker = HierarchicalChunker()
        self.dense_encoder = DenseEncoder()
        self.sparse_encoder = SparseBM25Encoder()
        self.store = QdrantStore()

    async def ingest_file(self, file_path: str | Path, req: IngestRequest) -> IngestResponse:
        file_path = Path(file_path)
        doc_id = str(uuid.uuid4())

        log.info("Ingesting %s  (state=%s lang=%s security=%s)", file_path.name, req.state, req.language, req.security_level)

        pages = self.ocr.extract(file_path, language=req.language)

        meta = DocumentMetadata(
            document_id=doc_id,
            filename=file_path.name,
            state=req.state,
            language=req.language,
            category=req.category,
            security_level=req.security_level,
            allowed_roles=req.allowed_roles,
            allowed_states=req.allowed_states,
            source_pages=len(pages),
        )

        chunks = self.chunker.chunk(pages, meta)
        parent_chunks = [c for c in chunks if c.chunk_type == "parent"]
        child_chunks = [c for c in chunks if c.chunk_type == "child"]

        texts = [c.text for c in chunks]
        dense_vectors = self.dense_encoder.encode(texts)
        sparse_vectors = [self.sparse_encoder.encode(t) for t in texts]

        await self.store.upsert_chunks(chunks, dense_vectors, sparse_vectors)

        log.info("Ingested %s: %d parents, %d children", file_path.name, len(parent_chunks), len(child_chunks))
        return IngestResponse(
            document_id=doc_id,
            filename=file_path.name,
            total_parent_chunks=len(parent_chunks),
            total_child_chunks=len(child_chunks),
        )

    async def ingest_directory(self, directory: str | Path, req: IngestRequest) -> list[IngestResponse]:
        directory = Path(directory)
        results: list[IngestResponse] = []
        for pdf in sorted(directory.glob("*.pdf")):
            per_file_req = req.model_copy(update={"path": str(pdf)})
            resp = await self.ingest_file(pdf, per_file_req)
            results.append(resp)
        return results
