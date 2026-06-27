"""Filename -> document metadata inference (state / language / category / security).

Pure functions with no OCR/embedding dependencies, so they're importable in
light contexts (e.g. the RBAC contract test) and reusable by the seed and the
ingest API alike.

The RBAC vocabularies below are a SECURITY CONTRACT shared with the query app's
``app/auth/rbac.py``. The seed may only emit these values; the query app filters
retrieval on them. Changing either set here requires a matching change there.
"""

from __future__ import annotations

from app.models.document import DocumentCategory

# Closed RBAC vocabularies — must stay in lockstep with the query app.
SECURITY_LEVELS: tuple[str, ...] = ("PUBLIC", "RESTRICTED", "CONFIDENTIAL")
ROLES: tuple[str, ...] = ("SPEAKER", "MLA", "MEDIA", "PUBLIC")
ALL_ROLES: list[str] = list(ROLES)


def language_for(name: str) -> str:
    upper = name.upper()
    if "_TE" in upper:
        return "te"
    if "_HI" in upper:
        return "hi"
    return "en"


def category_for(name: str) -> DocumentCategory:
    n = name.lower()
    if "appropriation" in n or "_bill" in n or "bill_" in n:
        return DocumentCategory.BILL
    if "_act" in n or "act_" in n or "policy_act" in n:
        return DocumentCategory.ACT
    if "debate" in n:
        return DocumentCategory.DEBATE_TRANSCRIPT
    if "committee" in n or "report" in n or "assessment" in n:
        return DocumentCategory.COMMITTEE_REPORT
    if "press_release" in n:
        return DocumentCategory.PRESS_RELEASE
    if "gazette" in n:
        return DocumentCategory.GAZETTE_NOTIFICATION
    if "_qa" in n or "question" in n:
        return DocumentCategory.QUESTION_ANSWER
    return DocumentCategory.GENERAL


def security_for(name: str) -> tuple[str, list[str]]:
    """Return (security_level, allowed_roles) inferred from the filename."""
    n = name.lower()
    if "confidential" in n:
        return "CONFIDENTIAL", ["SPEAKER"]
    if "committee" in n:
        return "RESTRICTED", ["SPEAKER", "MLA"]
    return "PUBLIC", list(ALL_ROLES)
