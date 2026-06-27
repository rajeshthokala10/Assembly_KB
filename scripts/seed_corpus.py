"""Seed the Qdrant collection with the bundled sample documents.

Unlike the ``/ingest/directory`` endpoint (which stamps one metadata blob onto
every file), this script derives per-file metadata from the folder + filename so
the mixed sample corpus (EN/TE/HI, AP/UP, PUBLIC/RESTRICTED/CONFIDENTIAL) is
labelled correctly and RBAC behaves as documented.

Run AFTER scripts/init_qdrant.py and with a populated .env:

    python scripts/seed_corpus.py
    python scripts/seed_corpus.py --reset      # recreate the collection first
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.ingestion.metadata import category_for, language_for, security_for
from app.ingestion.pipeline import IngestionPipeline
from app.models.document import IngestRequest
from app.vectorstore.qdrant_store import QdrantStore

SAMPLE_ROOT = Path(__file__).resolve().parent.parent / "data" / "sample_docs"


def _request_for(pdf: Path, state: str) -> IngestRequest:
    level, roles = security_for(pdf.name)
    return IngestRequest(
        path=str(pdf),
        state=state,
        language=language_for(pdf.name),
        category=category_for(pdf.name),
        security_level=level,
        allowed_roles=roles,
        allowed_states=[state],
    )


async def main(reset: bool, force: bool) -> None:
    store = QdrantStore()
    if reset:
        print(f"Recreating collection '{store.collection}'…")
        if store.client.collection_exists(store.collection):
            store.client.delete_collection(store.collection)
    store.ensure_collection()

    if not SAMPLE_ROOT.is_dir():
        sys.exit(f"Sample docs not found at {SAMPLE_ROOT}")

    pipeline = IngestionPipeline()
    pdfs = sorted(SAMPLE_ROOT.glob("*/*.pdf"))
    if not pdfs:
        sys.exit(f"No PDFs under {SAMPLE_ROOT}")

    # Incremental by default: each document is hashed and only (re)embedded if
    # new or changed. --reset rebuilds from scratch; --force re-ingests all.
    mode = "full rebuild" if reset else ("forced re-ingest" if force else "incremental (delta)")
    print(f"Seeding {len(pdfs)} documents into '{store.collection}'  [{mode}]…\n")
    print(f"{'FILE':<48} {'STATE':<5} {'LANG':<4} {'STATUS':<9} {'CHUNKS'}")
    print("-" * 100)

    tally = {"inserted": 0, "updated": 0, "skipped": 0}
    for pdf in pdfs:
        state = pdf.parent.name.upper()
        req = _request_for(pdf, state)
        # state/filename uniquely identifies the document across rebuilds.
        source = f"{pdf.parent.name}/{pdf.name}"
        resp = await pipeline.ingest_file(pdf, req, source_path=source, force=force)
        tally[resp.status] = tally.get(resp.status, 0) + 1
        chunks = f"{resp.total_parent_chunks}p/{resp.total_child_chunks}c" if resp.status != "skipped" else "—"
        print(f"{pdf.name:<48} {req.state:<5} {req.language:<4} {resp.status:<9} {chunks}")

    print(
        f"\nDone. inserted={tally['inserted']}  updated={tally['updated']}  "
        f"skipped={tally['skipped']}  (total {len(pdfs)})"
    )


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--reset", action="store_true", help="delete & recreate the collection, then ingest everything")
    ap.add_argument("--force", action="store_true", help="re-ingest every document even if unchanged")
    args = ap.parse_args()
    asyncio.run(main(args.reset, args.force))
