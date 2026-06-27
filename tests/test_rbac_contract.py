"""RBAC contract test — freezes the access-control vocabulary the seed emits.

The query app (separate repo, app/auth/rbac.py) filters retrieval on these exact
payload fields and values. If the seed starts emitting a new security tier or
role, or a field is renamed, this test fails on purpose: the change MUST be
mirrored in the query app, or access control silently leaks / over-restricts.

Dependency-light (pydantic only) — runs in the normal CI without the ML deps.
Run:  python tests/test_rbac_contract.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.ingestion.metadata import ROLES, SECURITY_LEVELS, security_for
from app.models.document import ChunkRecord

# The contract the query app's auth/rbac.py is built against.
EXPECTED_LEVELS = {"PUBLIC", "RESTRICTED", "CONFIDENTIAL"}
EXPECTED_ROLES = {"SPEAKER", "MLA", "MEDIA", "PUBLIC"}
RBAC_PAYLOAD_FIELDS = {"security_level", "allowed_roles", "allowed_states", "state"}


def test_vocabulary_frozen():
    assert set(SECURITY_LEVELS) == EXPECTED_LEVELS, "security tier vocabulary changed"
    assert set(ROLES) == EXPECTED_ROLES, "role vocabulary changed"


def test_security_inference_stays_in_vocabulary():
    # Every (level, roles) the seed can produce must use only known values.
    for name in (
        "AP_Confidential_Cabinet_Note_TE.pdf",          # confidential
        "AP_Committee_Report_Water_Resources_EN.pdf",   # restricted
        "AP_Appropriation_Bill_2025_EN.pdf",            # public
    ):
        level, roles = security_for(name)
        assert level in EXPECTED_LEVELS, f"{name} -> unknown level {level}"
        assert set(roles) <= EXPECTED_ROLES, f"{name} -> unknown roles {roles}"

    # Spot-check the actual policy mapping the query app relies on.
    assert security_for("x_confidential.pdf") == ("CONFIDENTIAL", ["SPEAKER"])
    assert security_for("x_committee.pdf") == ("RESTRICTED", ["SPEAKER", "MLA"])
    assert security_for("x_public.pdf")[0] == "PUBLIC"


def test_payload_carries_rbac_fields():
    fields = set(ChunkRecord.model_fields)
    missing = RBAC_PAYLOAD_FIELDS - fields
    assert not missing, f"ChunkRecord missing RBAC payload fields: {missing}"


if __name__ == "__main__":
    test_vocabulary_frozen()
    test_security_inference_stays_in_vocabulary()
    test_payload_carries_rbac_fields()
    print("✅ RBAC CONTRACT TEST PASSED")
