"""Indic-aware text normalization.

Indian scripts encode the same grapheme several ways (composed vs decomposed,
nukta variants) and carry zero-width joiners that split otherwise-identical
tokens. Normalizing consistently at BOTH ingest and query time keeps dense
embeddings and BM25 tokens aligned across Devanagari (Hindi) and Telugu.

The baseline (Unicode NFC + zero-width/whitespace cleanup) is dependency-free.
If the optional ``indic-nlp-library`` is installed, deeper script-aware
normalization is applied for hi/te.
"""

from __future__ import annotations

import re
import unicodedata
from functools import lru_cache

from app.config import settings

_WS = re.compile(r"\s+")
# ZWSP, ZWNJ, ZWJ, BOM — invisible characters that fragment Indic tokens.
_ZERO_WIDTH = dict.fromkeys((0x200B, 0x200C, 0x200D, 0xFEFF), None)


@lru_cache(maxsize=1)
def _indic_factory():
    """Return AI4Bharat's IndicNormalizerFactory if the library is present."""
    try:
        from indicnlp.normalize.indic_normalize import IndicNormalizerFactory

        return IndicNormalizerFactory()
    except Exception:  # library not installed — fall back to the NFC baseline
        return None


@lru_cache(maxsize=4)
def _indic_normalizer(lang: str):
    factory = _indic_factory()
    if factory is None:
        return None
    try:
        return factory.get_normalizer(lang)
    except Exception:
        return None


def normalize_indic(text: str, lang: str | None = None) -> str:
    """Normalize text for retrieval. Safe on English (NFC is a no-op there).

    ``lang`` ("hi"/"te") enables deeper script-aware normalization when the
    optional library is available; without it, the NFC baseline still applies.
    """
    if not text or not settings.indic_normalize:
        return text
    # Canonical composition collapses the many encodings of one grapheme.
    text = unicodedata.normalize("NFC", text)
    text = text.translate(_ZERO_WIDTH)
    if lang in ("hi", "te"):
        normalizer = _indic_normalizer(lang)
        if normalizer is not None:
            try:
                text = normalizer.normalize(text)
            except Exception:
                pass
    return _WS.sub(" ", text).strip()
