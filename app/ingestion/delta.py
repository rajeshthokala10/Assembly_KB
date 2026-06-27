"""Delta-ingestion helpers: content hashing + stable document identity.

A document's identity across rebuilds is its *logical source path* (e.g.
``AP/AP_Assembly_Debate_12_01_2020_TE.pdf``), mapped to a deterministic
``document_id`` via uuid5. Its *version* is the SHA-256 of the file bytes. The
ingestion pipeline compares the stored hash in Qdrant against the current file
hash to decide skip / update / insert — so unchanged documents are never
re-OCR'd or re-embedded.
"""

from __future__ import annotations

import hashlib
import uuid
from pathlib import Path

# Fixed namespace so a given source_path always yields the same document_id.
_DOC_NAMESPACE = uuid.UUID("a1b2c3d4-e5f6-4a5b-8c9d-000000000001")

_READ_BLOCK = 1 << 20  # 1 MiB streaming read — handles large scanned PDFs


def file_content_hash(path: str | Path) -> str:
    """SHA-256 of a file's bytes — the document's content fingerprint."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(_READ_BLOCK), b""):
            h.update(block)
    return h.hexdigest()


def document_id_for(source_path: str) -> str:
    """Stable document id derived from a logical source path (uuid5)."""
    return str(uuid.uuid5(_DOC_NAMESPACE, source_path))
