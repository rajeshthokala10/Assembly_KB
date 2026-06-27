# Assembly-KB — Ingestion & Knowledge Base

Standalone **ingestion service** for the Assembly-KB legislative RAG system. It
owns the corpus and everything that writes to Qdrant: OCR (incl. legacy-font
Indic), hierarchical chunking, multilingual embeddings (BGE-M3 dense + BM25
sparse), Indic normalization, and the Qdrant collection schema.

It is split from the query/API app so the heavy embedding model (~2.3 GB) and
batch OCR never share the always-on web container's memory.

## Layout

```
app/
├── config.py                # Pydantic settings (.env)
├── models/document.py       # Document/Chunk metadata, ingest models
├── ingestion/
│   ├── ocr_engine.py        # PDF text + Tesseract OCR (tel/hin/eng), legacy-font detection
│   ├── chunker.py           # Hierarchical parent/child chunking
│   ├── embeddings.py        # Dense (BGE-M3) + sparse (BM25)  — applies Indic normalization
│   ├── text_normalize.py    # NFC + zero-width cleanup (+ IndicNLP if installed)
│   └── pipeline.py          # End-to-end ingest orchestrator
└── vectorstore/qdrant_store.py   # Collection schema, indices, upsert

scripts/
├── init_qdrant.py           # Create the collection + payload indices
├── seed_corpus.py           # Seed data/sample_docs/ (idempotent; --reset / --force)
└── generate_sample_docs.py  # Regenerate the bundled sample PDFs

data/sample_docs/            # The bundled knowledge base (AP/UP, EN/TE/HI)
.github/workflows/reseed.yml # On-demand reseed (manual workflow_dispatch)
```

## ⚠️ Shared contract with the query app

These MUST match the query/API app exactly, or retrieval silently breaks:

| Setting | Must equal the query side |
|---|---|
| `EMBEDDING_MODEL` / `EMBEDDING_DIM` | same model + dimensions |
| Qdrant collection name + vector/index schema (`qdrant_store.py`) | identical |
| `INDIC_NORMALIZE` and chunking params | identical |

Treat `config.py` + `qdrant_store.py` as the source of truth; keep them in sync
with the query app (ideally extract a shared package later).

## Usage

```bash
cp .env.example .env          # set QDRANT_URL, QDRANT_API_KEY, etc.
pip install -r requirements.txt
python scripts/init_qdrant.py         # ensure collection exists
python scripts/seed_corpus.py         # incremental: only new/changed docs
python scripts/seed_corpus.py --force # re-ingest every document
python scripts/seed_corpus.py --reset # wipe + rebuild from scratch
```

Or via Docker / the `reseed.yml` workflow (needs `QDRANT_URL` + `QDRANT_API_KEY`).

## Incremental ingestion (delta updates)

Re-running the seed only touches what changed. Each document is identified by a
stable `document_id` (uuid5 of its `state/filename` source path) and versioned by
a **SHA-256 of its bytes**, both stored in every chunk's Qdrant payload. Before
any OCR or embedding, the pipeline compares the stored hash to the file's hash:

| Stored vs current | Action |
|---|---|
| hash matches | **skip** — no OCR, no embedding, no cost |
| hash differs | **update** — delete the doc's old chunks, then re-ingest |
| no stored hash | **insert** — embed and ingest |

So a second build ingests only new/modified documents and never duplicates
unchanged data. `--force` re-ingests everything; `--reset` wipes first.
