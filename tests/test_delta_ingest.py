"""End-to-end check of delta ingestion (skip / update / insert).

Runs against an in-memory Qdrant with fake OCR + encoders, so it needs neither
the cloud cluster nor the BGE-M3 model. Run:  python tests/test_delta_ingest.py
"""

from __future__ import annotations

import asyncio
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from qdrant_client import QdrantClient

import app.vectorstore.qdrant_store as qs
import app.ingestion.pipeline as pl

# ── Wire up lightweight test doubles ─────────────────────────────────────────
_MEM = QdrantClient(":memory:")
qs.get_qdrant_client = lambda: _MEM          # all stores share one in-memory DB
qs.settings.embedding_dim = 8                # match the fake dense vectors


class _FakeOCR:
    def extract(self, path, language="en"):
        return [{"page": 1, "text": Path(path).read_text(encoding="utf-8")}]


class _FakeDense:
    dim = 8
    def encode(self, texts):           # noqa: D401
        return [[0.1] * 8 for _ in texts]
    def encode_single(self, text):
        return [0.1] * 8


class _FakeSparse:
    def encode(self, text):
        return ([1, 2, 3], [1.0, 1.0, 1.0])


pl.OCREngine = _FakeOCR
pl.DenseEncoder = _FakeDense
pl.SparseBM25Encoder = _FakeSparse

from app.ingestion.pipeline import IngestionPipeline          # noqa: E402
from app.models.document import DocumentCategory, IngestRequest  # noqa: E402


def _points_for(store, document_id: int) -> int:
    from qdrant_client import models as m
    pts, _ = store.client.scroll(
        collection_name=store.collection,
        scroll_filter=m.Filter(must=[m.FieldCondition(key="document_id", match=m.MatchValue(value=document_id))]),
        limit=1000, with_payload=False, with_vectors=False,
    )
    return len(pts)


async def main() -> None:
    pipe = IngestionPipeline()
    req = IngestRequest(path="x", state="AP", language="en",
                        category=DocumentCategory.GENERAL, security_level="PUBLIC")

    d = Path(tempfile.mkdtemp())
    doc = d / "doc1.txt"
    doc.write_text("assembly budget allocation 2025 " * 60, encoding="utf-8")

    r1 = await pipe.ingest_file(doc, req, source_path="AP/doc1")
    r2 = await pipe.ingest_file(doc, req, source_path="AP/doc1")          # unchanged
    n_after_skip = _points_for(pipe.store, r1.document_id)

    doc.write_text("assembly budget allocation 2026 amended figures " * 60, encoding="utf-8")
    r3 = await pipe.ingest_file(doc, req, source_path="AP/doc1")          # changed
    n_after_update = _points_for(pipe.store, r3.document_id)

    doc2 = d / "doc2.txt"
    doc2.write_text("new gazette notification land revenue " * 60, encoding="utf-8")
    r4 = await pipe.ingest_file(doc2, req, source_path="AP/doc2")         # new

    print(f"insert : {r1.status:8} ({r1.total_parent_chunks}p/{r1.total_child_chunks}c)")
    print(f"skip   : {r2.status:8} (no re-embed)")
    print(f"update : {r3.status:8} ({r3.total_parent_chunks}p/{r3.total_child_chunks}c)")
    print(f"insert2: {r4.status:8}")
    insert_chunks = r1.total_parent_chunks + r1.total_child_chunks
    update_chunks = r3.total_parent_chunks + r3.total_child_chunks
    print(f"same document_id across rebuilds: {r1.document_id == r3.document_id}")
    print(f"doc1 points after skip:   {n_after_skip} (== insert chunks {insert_chunks})")
    print(f"doc1 points after update: {n_after_update} (== update chunks {update_chunks}, old ones deleted)")

    assert r1.status == "inserted"
    assert r2.status == "skipped"
    assert r3.status == "updated"
    assert r4.status == "inserted"
    assert r1.document_id == r3.document_id              # stable identity across rebuilds
    assert n_after_skip == insert_chunks                # skip added nothing
    assert n_after_update == update_chunks              # update replaced cleanly — no orphans/dupes
    print("\n✅ DELTA TEST PASSED")


if __name__ == "__main__":
    asyncio.run(main())
