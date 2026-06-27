from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class DocumentCategory(str, Enum):
    BILL = "BILL"
    ACT = "ACT"
    DEBATE_TRANSCRIPT = "DEBATE_TRANSCRIPT"
    COMMITTEE_REPORT = "COMMITTEE_REPORT"
    PRESS_RELEASE = "PRESS_RELEASE"
    GAZETTE_NOTIFICATION = "GAZETTE_NOTIFICATION"
    QUESTION_ANSWER = "QUESTION_ANSWER"
    GENERAL = "GENERAL"


class DocumentMetadata(BaseModel):
    document_id: str
    filename: str
    state: str = Field(..., description="AP | UP | ALL")
    language: str = Field(..., description="en | te | hi")
    category: DocumentCategory = DocumentCategory.GENERAL
    security_level: str = Field(default="PUBLIC", description="PUBLIC | RESTRICTED | CONFIDENTIAL")
    allowed_roles: list[str] = Field(default_factory=lambda: ["SPEAKER", "MLA", "MEDIA", "PUBLIC"])
    allowed_states: list[str] = Field(default_factory=lambda: ["AP", "UP", "ALL"])
    title: str = ""
    year: int | None = None
    source_pages: int = 0
    # Delta tracking: logical path identifying the document across rebuilds, and
    # the SHA-256 of its bytes identifying the current version.
    source_path: str = ""
    content_hash: str = ""


class ChunkRecord(BaseModel):
    chunk_id: str
    document_id: str
    parent_chunk_id: Optional[str] = None
    prev_chunk_id: Optional[str] = None
    next_chunk_id: Optional[str] = None
    chunk_index: int = 0
    chunk_type: str = Field(default="child", description="parent | child")
    text: str
    state: str
    language: str
    category: str
    security_level: str
    allowed_roles: list[str]
    allowed_states: list[str]
    page_number: int | None = None
    # Carried into the Qdrant payload so delta checks can read them back.
    source_path: str = ""
    content_hash: str = ""


class IngestRequest(BaseModel):
    path: str = Field(..., description="File or directory path")
    state: str = Field(..., pattern=r"^(AP|UP|ALL)$")
    language: str = Field(..., pattern=r"^(en|te|hi)$")
    category: DocumentCategory = DocumentCategory.GENERAL
    security_level: str = Field(default="PUBLIC", pattern=r"^(PUBLIC|RESTRICTED|CONFIDENTIAL)$")
    allowed_roles: list[str] = Field(default_factory=lambda: ["SPEAKER", "MLA", "MEDIA", "PUBLIC"])
    allowed_states: list[str] = Field(default_factory=lambda: ["AP", "UP", "ALL"])


class IngestResponse(BaseModel):
    document_id: str
    filename: str
    total_parent_chunks: int
    total_child_chunks: int
    status: str = "success"
