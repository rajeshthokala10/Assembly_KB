from __future__ import annotations

import hashlib
import logging
import math
from collections import Counter
from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import settings
from app.ingestion.text_normalize import normalize_indic

log = logging.getLogger(__name__)


# BGE-M3 ships with max_seq_length=8192. Attention memory is O(n²), so leaving
# it at 8192 on CPU explodes a long chunk into a multi-GiB allocation. Cap it to
# a chunk-appropriate window — our parent chunks are ~1500 chars, well under this.
_MAX_SEQ_LENGTH = 512
_ENCODE_BATCH_SIZE = 16


@lru_cache(maxsize=1)
def _load_model() -> SentenceTransformer:
    log.info("Loading embedding model: %s", settings.embedding_model)
    model = SentenceTransformer(settings.embedding_model)
    if model.max_seq_length is None or model.max_seq_length > _MAX_SEQ_LENGTH:
        model.max_seq_length = _MAX_SEQ_LENGTH
    return model


class DenseEncoder:
    """Multilingual dense embeddings via sentence-transformers."""

    def __init__(self) -> None:
        self.model = _load_model()
        self.dim = settings.embedding_dim

    def encode(self, texts: list[str]) -> list[list[float]]:
        # Normalize symmetrically with query-time encoding (Indic NFC cleanup).
        texts = [normalize_indic(t) for t in texts]
        vecs = self.model.encode(
            texts,
            show_progress_bar=False,
            normalize_embeddings=True,
            batch_size=_ENCODE_BATCH_SIZE,
        )
        return vecs.tolist()

    def encode_single(self, text: str) -> list[float]:
        return self.encode([text])[0]


class SparseBM25Encoder:
    """Hash-based BM25 sparse encoder — no global vocabulary needed."""

    def __init__(self, vocab_size: int = 30_000, k1: float = 1.5, b: float = 0.75) -> None:
        self.vocab_size = vocab_size
        self.k1 = k1
        self.b = b
        self.avg_dl = 256.0

    def _tokenize(self, text: str) -> list[str]:
        return text.lower().split()

    def _hash_token(self, token: str) -> int:
        return int(hashlib.sha256(token.encode()).hexdigest(), 16) % self.vocab_size

    def encode(self, text: str) -> tuple[list[int], list[float]]:
        tokens = self._tokenize(normalize_indic(text))
        if not tokens:
            return [], []
        tf = Counter(tokens)
        dl = len(tokens)

        index_map: dict[int, float] = {}
        for token, count in tf.items():
            idx = self._hash_token(token)
            score = (count * (self.k1 + 1)) / (count + self.k1 * (1 - self.b + self.b * dl / self.avg_dl))
            if idx in index_map:
                index_map[idx] = max(index_map[idx], score)
            else:
                index_map[idx] = score

        indices = sorted(index_map.keys())
        values = [index_map[i] for i in indices]
        return indices, values
