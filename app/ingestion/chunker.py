from __future__ import annotations

from dataclasses import dataclass

from app.config import settings
from app.models.document import ChunkRecord, DocumentMetadata


@dataclass
class _WordSpan:
    """A word-window chunk plus the index of its first word in the source."""

    text: str
    start_word: int


def _split_tokens(words: list[str], size: int, overlap: int, base: int = 0) -> list[_WordSpan]:
    """Sliding word-window split with overlap, tracking each window's start.

    ``base`` offsets the reported start_word so children can report their
    position relative to the *full document*, not just their parent.
    """
    if size <= 0:
        raise ValueError("chunk size must be positive")
    # Guard against a non-advancing window (would otherwise loop forever).
    step = max(1, size - overlap)

    spans: list[_WordSpan] = []
    start = 0
    while start < len(words):
        end = start + size
        spans.append(_WordSpan(text=" ".join(words[start:end]), start_word=base + start))
        start += step
    return spans


class HierarchicalChunker:
    """Two-tier parent/child chunking with sequential linkage and page mapping."""

    def __init__(
        self,
        parent_size: int | None = None,
        child_size: int | None = None,
        overlap: int | None = None,
    ) -> None:
        self.parent_size = parent_size or settings.parent_chunk_size
        self.child_size = child_size or settings.child_chunk_size
        self.overlap = overlap or settings.chunk_overlap

    def chunk(self, pages: list[dict], meta: DocumentMetadata) -> list[ChunkRecord]:
        # Build a word list and an aligned word->page map. full_text.split() and
        # the concatenation of each page's words yield the same sequence, so the
        # indices line up exactly.
        words: list[str] = []
        word_page: list[int] = []
        for p in pages:
            page_words = p["text"].split()
            words.extend(page_words)
            word_page.extend([p["page"]] * len(page_words))

        def page_for(word_idx: int) -> int | None:
            if not word_page:
                return None
            return word_page[min(word_idx, len(word_page) - 1)]

        all_records: list[ChunkRecord] = []
        prev_child_id: str | None = None

        parent_spans = _split_tokens(words, self.parent_size, self.overlap)
        for p_idx, p_span in enumerate(parent_spans):
            parent_id = f"{meta.document_id}::p{p_idx}"
            parent_rec = self._make_record(
                parent_id, meta, p_span.text, "parent", p_idx, page_for(p_span.start_word)
            )
            all_records.append(parent_rec)

            parent_words = p_span.text.split()
            child_spans = _split_tokens(parent_words, self.child_size, self.overlap, base=p_span.start_word)
            child_ids = [f"{parent_id}::c{c_idx}" for c_idx in range(len(child_spans))]

            for c_idx, c_span in enumerate(child_spans):
                cid = child_ids[c_idx]
                next_id = child_ids[c_idx + 1] if c_idx + 1 < len(child_ids) else None
                rec = self._make_record(
                    cid, meta, c_span.text, "child", c_idx, page_for(c_span.start_word),
                    parent_chunk_id=parent_id,
                    prev_chunk_id=prev_child_id,
                    next_chunk_id=next_id,
                )
                all_records.append(rec)
                prev_child_id = cid

        return all_records

    def _make_record(
        self,
        chunk_id: str,
        meta: DocumentMetadata,
        text: str,
        chunk_type: str,
        index: int,
        page_number: int | None,
        **kwargs,
    ) -> ChunkRecord:
        return ChunkRecord(
            chunk_id=chunk_id,
            document_id=meta.document_id,
            chunk_index=index,
            chunk_type=chunk_type,
            text=text,
            state=meta.state,
            language=meta.language,
            category=meta.category.value,
            security_level=meta.security_level,
            allowed_roles=meta.allowed_roles,
            allowed_states=meta.allowed_states,
            page_number=page_number,
            source_path=meta.source_path,
            content_hash=meta.content_hash,
            **kwargs,
        )
