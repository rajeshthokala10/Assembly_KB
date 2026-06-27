from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # JWT
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480

    # CORS — explicit allow-list (wildcard is incompatible with credentials)
    cors_allow_origins: list[str] = [
        "http://localhost:8501", "http://localhost:8000",
        "http://localhost:5173", "http://127.0.0.1:5173",  # React/Vite dev UI
    ]

    # Qdrant
    # For Qdrant Cloud set qdrant_url to the full https cluster endpoint and
    # qdrant_api_key. For a local/self-hosted instance leave qdrant_url empty
    # and use qdrant_host/qdrant_port instead.
    qdrant_url: str | None = None
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_api_key: str | None = None
    qdrant_collection: str = "assembly_kb"
    # Client timeout (seconds) for connect + read. Kept generous so a slow TLS
    # handshake to a distant Cloud region (e.g. Railway in Singapore reaching a
    # sa-east-1 cluster) doesn't surface as a 500. Override with QDRANT_TIMEOUT.
    qdrant_timeout: float = 60.0

    # Embedding
    embedding_model: str = "BAAI/bge-m3"
    embedding_dim: int = 1024

    # Indic text normalization — NFC + zero-width cleanup applied symmetrically at
    # ingest and query time (deeper script-aware normalization when the optional
    # indic-nlp-library is installed). Improves Devanagari/Telugu match consistency.
    indic_normalize: bool = True

    # Reranking — a multilingual cross-encoder re-scores the top hybrid candidates
    # for a precision boost (esp. cross-lingual Indic). Off by default because it
    # loads a second model (~2 GB RAM); enable with RERANK_ENABLED=true.
    rerank_enabled: bool = False
    rerank_model: str = "BAAI/bge-reranker-v2-m3"
    rerank_candidates: int = 50  # hybrid hits fetched, then reranked down to top_k

    # LLM
    # llm_provider selects the active backend: "openai" or "anthropic".
    llm_provider: str = "openai"
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    # Model used when the provider is OpenAI (e.g. gpt-4o, gpt-4o-mini).
    openai_model: str = "gpt-4o"
    # Model used when the provider is Anthropic.
    llm_model: str = "claude-sonnet-4-20250514"
    llm_max_tokens: int = 2048

    # Logging
    log_dir: str = "logs"
    log_file: str = "assembly_kb.log"
    log_level: str = "INFO"

    # Tesseract
    tesseract_cmd: str = "/usr/bin/tesseract"

    # Analytics + feedback store (SQLite). Point at a mounted volume for
    # persistence across deploys.
    analytics_db: str = "data/analytics.db"

    # Chunking
    parent_chunk_size: int = 1500
    child_chunk_size: int = 300
    chunk_overlap: int = 50


settings = Settings()
