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
├── seed_corpus.py           # Seed data/sample_docs/ (incremental delta; --force / --reset)
└── generate_sample_docs.py  # Regenerate the bundled sample PDFs

data/sample_docs/            # The bundled knowledge base (AP/UP, EN/TE/HI)
.github/workflows/reseed.yml # On-demand reseed (manual workflow_dispatch)
```

## How this repo and the query app fit together

This repo (**Assembly_KB**) and the query app (**Assembly-Assistant**) never call
each other. They communicate **only through the Qdrant collection** — this repo
*writes* vectors + access labels; the query app *reads* and *enforces* them:

```
  Assembly_KB  (write / ingest)                 Assembly-Assistant  (read / serve)
  ─────────────────────────────                 ──────────────────────────────────
  PDF → OCR → chunk → embed                       user query → embed
      → stamp payload labels   ──▶   Qdrant   ◀── → RBAC filter on those labels
        (security_level,                            (auth/rbac.build_qdrant_filter)
         allowed_roles, state)
```

Because there is no API between them, a handful of values form a **contract**
both sides must agree on. A mismatch fails silently — no error, just wrong or
missing results — so the contract is documented and CI-checked.

### Retrieval contract — must be identical on both sides

| Setting | Source of truth (here) |
|---|---|
| `EMBEDDING_MODEL` / `EMBEDDING_DIM` | `config.py` — the query must embed with the same model/dims |
| Qdrant collection name + vector/index schema | `qdrant_store.py` |
| `INDIC_NORMALIZE` + chunking params | `config.py` (applied symmetrically at query time) |

### RBAC contract — security-sensitive

The access vocabulary lives in **`app/ingestion/metadata.py`** (`SECURITY_LEVELS`,
`ROLES`, `security_for()`); the query app's **`app/auth/rbac.py`** filters on these
exact values. **`tests/test_rbac_contract.py`** freezes them, so CI fails if the
labels here drift from what the query app enforces.

| Payload field | Written here (`metadata.security_for` + models) | Read by query app (`auth/rbac`) |
|---|---|---|
| `security_level` | `PUBLIC` / `RESTRICTED` / `CONFIDENTIAL` | filters to the user's allowed levels |
| `allowed_roles`  | `SPEAKER` / `MLA` / `MEDIA` / `PUBLIC`   | requires the user's role to be present |
| `state` / `allowed_states` | `AP` / `UP` / `ALL`            | scopes non-privileged roles to their state |

Filename → labels (in `metadata.security_for`): `confidential` → CONFIDENTIAL
(SPEAKER only); `committee` → RESTRICTED (SPEAKER + MLA); everything else →
PUBLIC. **Change a tier, role, or field name here → update `app/auth/rbac.py` in
the query app in lockstep** (the contract test will flag the drift).

## Running the seed

### 1. Prerequisites

OCR system tools the pipeline shells out to:

```bash
# macOS
brew install tesseract tesseract-lang poppler
# Debian / Ubuntu
sudo apt-get install -y tesseract-ocr tesseract-ocr-tel tesseract-ocr-hin \
                        tesseract-ocr-eng poppler-utils
```

Python deps + a configured `.env`:

```bash
pip install -r requirements.txt
cp .env.example .env      # then set QDRANT_URL + QDRANT_API_KEY (use rotated keys!)
```

- `EMBEDDING_MODEL` / `EMBEDDING_DIM` / `QDRANT_COLLECTION` **must match the query app**.
- Have **~4 GB RAM free** — the first run downloads BGE-M3 (~2.3 GB) into memory.

### 2. Seed it

```bash
python scripts/init_qdrant.py          # create collection + indices (one-time, idempotent)

python scripts/seed_corpus.py          # incremental (default): only new/changed docs
python scripts/seed_corpus.py --force  # re-ingest every document
python scripts/seed_corpus.py --reset  # wipe the collection, then rebuild from scratch
```

The default is **incremental** — re-running ingests only new or modified files
(see [Incremental ingestion](#incremental-ingestion-delta-updates)). Each run
ends with a tally: `inserted=… updated=… skipped=…`.

> First run after switching to the hash-based identity scheme: run once with
> `--reset` so older points (random ids, no content hash) are rebuilt cleanly.
> Every run after that is true delta.

### 3. Add a document to the corpus

Drop the PDF under `data/sample_docs/<STATE>/` with a language suffix, then re-seed:

```
data/sample_docs/AP/AP_<Title>_<DD.MM.YYYY>_TE.pdf     #  _TE Telugu · _HI Hindi · _EN English
```

The filename drives the metadata: the folder → state (`AP`/`UP`), the
`_TE`/`_HI`/`_EN` suffix → language (so Indic PDFs get the right OCR model), and
keywords (`confidential`, `committee`, `bill`, `gazette`, …) → security level +
category. Then `python scripts/seed_corpus.py` ingests just the new file.

### 4. Run in Docker

```bash
docker build -t assembly-kb-ingest .
# init + incremental seed (the image's default command)
docker run --rm --env-file .env assembly-kb-ingest
# full rebuild
docker run --rm --env-file .env assembly-kb-ingest \
  sh -c "python scripts/init_qdrant.py && python scripts/seed_corpus.py --reset"
```

### 5. Run via GitHub Actions (no local setup)

Add repo secrets `QDRANT_URL` + `QDRANT_API_KEY`, then **Actions → "Reseed Qdrant
corpus" → Run workflow** (`reset: true`, `confirm: RESEED`). It runs on a CI
runner, so no local RAM or OCR install is needed.

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
