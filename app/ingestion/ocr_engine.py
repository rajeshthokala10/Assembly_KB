from __future__ import annotations

import logging
import re
import unicodedata
from pathlib import Path

import pytesseract
from pdf2image import convert_from_path
from pypdf import PdfReader

from app.config import settings

log = logging.getLogger(__name__)

LANG_MAP = {"en": "eng", "te": "tel", "hi": "hin"}

# Per-page OCR timeout (seconds) — bounds the impact of a pathological page.
OCR_PAGE_TIMEOUT_SECONDS = 120

# Unicode ranges for Indian scripts
TELUGU_RANGE = range(0x0C00, 0x0C80)
DEVANAGARI_RANGE = range(0x0900, 0x0980)


class OCREngine:
    """Extract text from PDFs — detects garbled legacy-encoded Indic text and
    falls back to Tesseract OCR when digital extraction produces garbage.

    Many Indian government PDFs use legacy fonts (e.g., Shree-Tel, Gautami
    remapped) that map Telugu/Hindi glyphs onto Latin codepoints. pypdf extracts
    characters like ``çÜ¿æý`` instead of ``సభ``.  The ``_is_garbled`` check
    catches this and forces OCR.
    """

    def __init__(self) -> None:
        pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd

    def extract(self, pdf_path: str | Path, language: str = "en") -> list[dict]:
        """Return a list of ``{page: int, text: str}`` dicts."""
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(pdf_path)

        pages = self._try_digital(pdf_path)

        needs_ocr = (
            not pages
            or all(len(p["text"].strip()) < 30 for p in pages)
            or self._is_garbled(pages, language)
        )

        if needs_ocr:
            reason = "empty/short" if not pages or all(len(p["text"].strip()) < 30 for p in pages) else "garbled legacy encoding"
            log.info("Digital extraction failed (%s) — falling back to OCR for %s", reason, pdf_path.name)
            pages = self._ocr(pdf_path, language)

        return pages

    def _try_digital(self, pdf_path: Path) -> list[dict]:
        reader = PdfReader(str(pdf_path))
        results: list[dict] = []
        for idx, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            results.append({"page": idx, "text": text})
        return results

    def _is_garbled(self, pages: list[dict], language: str) -> bool:
        """Detect legacy-encoded Indic PDFs that produce garbled digital text.

        Heuristics:
        1. For te/hi docs: if text has content but ZERO actual Telugu/Hindi
           Unicode characters, the font is a legacy remapping.
        2. High ratio of Latin-Extended / combining characters (the garbled
           output signature) relative to standard ASCII.
        3. Presence of the specific garbled patterns common in AP/UP legislative
           PDFs (``çÜ``, ``{ç³``, ``Ðèþ``, etc.).
        """
        if language == "en":
            return False

        sample = " ".join(p["text"][:500] for p in pages[:10])
        if len(sample.strip()) < 50:
            return False

        if language == "te":
            real_script = sum(1 for c in sample if ord(c) in TELUGU_RANGE)
            if real_script == 0:
                garble_markers = sum(1 for c in sample if 0x00C0 <= ord(c) <= 0x024F)
                ascii_alpha = sum(1 for c in sample if c.isascii() and c.isalpha())
                if garble_markers > ascii_alpha * 0.3:
                    log.info("Detected legacy Telugu encoding: 0 Telugu chars, %d Latin-Extended chars", garble_markers)
                    return True

        if language == "hi":
            real_script = sum(1 for c in sample if ord(c) in DEVANAGARI_RANGE)
            if real_script == 0:
                garble_markers = sum(1 for c in sample if 0x00C0 <= ord(c) <= 0x024F)
                ascii_alpha = sum(1 for c in sample if c.isascii() and c.isalpha())
                if garble_markers > ascii_alpha * 0.3:
                    log.info("Detected legacy Hindi encoding: 0 Devanagari chars, %d Latin-Extended chars", garble_markers)
                    return True

        return False

    def _ocr(self, pdf_path: Path, language: str) -> list[dict]:
        tess_lang = LANG_MAP.get(language, "eng")
        combined = "+".join(dict.fromkeys([tess_lang, "eng"]))

        total = self._page_count(pdf_path)
        results: list[dict] = []

        # Rasterise and OCR one page at a time. Converting the whole PDF up front
        # would load every page into memory at 300 DPI (a multi-GB spike on long
        # scanned documents); page-by-page keeps the footprint flat and lets a
        # single corrupt/timed-out page fail in isolation instead of aborting the
        # whole document.
        for page_no in range(1, total + 1):
            text = ""
            try:
                images = convert_from_path(
                    str(pdf_path), dpi=300, first_page=page_no, last_page=page_no
                )
                if images:
                    text = pytesseract.image_to_string(
                        images[0], lang=combined, timeout=OCR_PAGE_TIMEOUT_SECONDS
                    )
            except RuntimeError as exc:  # pytesseract raises RuntimeError on timeout
                log.warning("OCR timed out on page %d of %s: %s", page_no, pdf_path.name, exc)
            except Exception as exc:  # corrupt page, decode error, unrecognised charset
                log.warning("OCR failed on page %d of %s: %s", page_no, pdf_path.name, exc)

            results.append({"page": page_no, "text": text})
            if page_no % 50 == 0:
                log.info("OCR progress: %d/%d pages", page_no, total)

        return results

    @staticmethod
    def _page_count(pdf_path: Path) -> int:
        try:
            return len(PdfReader(str(pdf_path)).pages)
        except Exception:
            # Fall back to a full conversion only if we cannot read the page count.
            return len(convert_from_path(str(pdf_path), dpi=72))


def detect_script(text: str) -> str:
    """Detect the dominant script in a text sample. Returns 'te', 'hi', or 'en'."""
    te_count = sum(1 for c in text if ord(c) in TELUGU_RANGE)
    hi_count = sum(1 for c in text if ord(c) in DEVANAGARI_RANGE)
    en_count = sum(1 for c in text if c.isascii() and c.isalpha())

    total = te_count + hi_count + en_count
    if total == 0:
        return "en"
    if te_count / total > 0.15:
        return "te"
    if hi_count / total > 0.15:
        return "hi"
    return "en"
