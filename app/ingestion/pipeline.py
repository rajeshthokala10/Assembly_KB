from __future__ import annotations

import logging
from pathlib import Path

from app.ingestion.chunker import HierarchicalChunker
from app.ingestion.delta import document_id_for, file_content_hash
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

    async def ingest_file(
        self,
        file_path: str | Path,
        req: IngestRequest,
        source_path: str | None = None,
        force: bool = False,
    ) -> IngestResponse:
        """Incrementally ingest one document.

        Delta logic (skip / update / insert) runs BEFORE any OCR or embedding,
        so unchanged documents cost nothing:
          - stored hash == current hash  -> skip (status="skipped")
          - stored hash != current hash  -> delete old chunks, re-ingest ("updated")
          - no stored hash               -> ingest ("inserted")
        ``force=True`` re-ingests regardless of the stored hash.
        """
        file_path = Path(file_path)
        # Stable identity across rebuilds + content fingerprint for this version.
        source = source_path or file_path.name
        content_hash = file_content_hash(file_path)
        doc_id = document_id_for(source)

        self.store.ensure_collection()
        stored_hash = self.store.document_content_hash(doc_id)

        if stored_hash == content_hash and not force:
            log.info("Skipping unchanged %s", source)
            return IngestResponse(
                document_id=doc_id,
                filename=file_path.name,
                total_parent_chunks=0,
                total_child_chunks=0,
                status="skipped",
            )

        status = "updated" if stored_hash is not None else "inserted"
        if stored_hash is not None:
            # Content changed (or forced): drop the document's old vectors first
            # so a re-chunk with a different chunk count leaves no orphans.
            log.info("Replacing %s (%s)", source, "forced" if force else "content changed")
            self.store.delete_document(doc_id)

        log.info("Ingesting %s  (state=%s lang=%s security=%s)", source, req.state, req.language, req.security_level)
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
            source_path=source,
            content_hash=content_hash,
        )

        chunks = self.chunker.chunk(pages, meta)
        parent_chunks = [c for c in chunks if c.chunk_type == "parent"]
        child_chunks = [c for c in chunks if c.chunk_type == "child"]

        texts = [c.text for c in chunks]
        dense_vectors = self.dense_encoder.encode(texts)
        sparse_vectors = [self.sparse_encoder.encode(t) for t in texts]

        await self.store.upsert_chunks(chunks, dense_vectors, sparse_vectors)

        log.info("Ingested %s (%s): %d parents, %d children", source, status, len(parent_chunks), len(child_chunks))
        return IngestResponse(
            document_id=doc_id,
            filename=file_path.name,
            total_parent_chunks=len(parent_chunks),
            total_child_chunks=len(child_chunks),
            status=status,
        )

    async def ingest_directory(
        self, directory: str | Path, req: IngestRequest, force: bool = False
    ) -> list[IngestResponse]:
        directory = Path(directory)
        results: list[IngestResponse] = []
        for pdf in sorted(directory.glob("*.pdf")):
            per_file_req = req.model_copy(update={"path": str(pdf)})
            resp = await self.ingest_file(pdf, per_file_req, source_path=pdf.name, force=force)
            results.append(resp)
        return results
