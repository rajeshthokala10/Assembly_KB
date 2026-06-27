# Ingestion / knowledge-base worker for Assembly-KB.
# Heavy, batch, occasional — kept separate from the always-on web API so the
# embedding model (BGE-M3, ~2.3 GB) never shares the API container's memory.
FROM python:3.11-slim

# OCR system deps: Tesseract (en/te/hi legacy-font Indic) + Poppler for PDFs.
RUN apt-get update && apt-get install -y --no-install-recommends \
        tesseract-ocr \
        tesseract-ocr-tel \
        tesseract-ocr-hin \
        tesseract-ocr-eng \
        poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default: ensure the collection exists, then seed idempotently (no-op if the
# corpus is already present). Override the command to run --reset, etc.
CMD ["sh", "-c", "python scripts/init_qdrant.py && python scripts/seed_corpus.py"]
