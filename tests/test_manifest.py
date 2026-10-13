from pathlib import Path

import pytest

from hermes_instruction_pack.manifest import Manifest, sha256_bytes


def test_upsert_and_counts(tmp_path: Path):
    m = Manifest.load(tmp_path / "manifest.yaml")
    m.upsert(
        {
            "id": "x1",
            "kind": "gist",
            "url": "http://example",
            "status": "fetched",
            "audit_status": "pending",
        }
    )
    m.upsert(
        {
            "id": "x1",
            "kind": "gist",
            "url": "http://example",
            "status": "fetched",
            "audit_status": "reviewed",
        }
    )
    assert len(m.all()) == 1
    assert m.get("x1")["audit_status"] == "reviewed"
    assert m.counts() == {"total": 1, "fetched": 1}
    m.save()
    m2 = Manifest.load(tmp_path / "manifest.yaml")
    assert m2.get("x1")["url"] == "http://example"


def test_missing_required_fields(tmp_path: Path):
    m = Manifest.load(tmp_path / "manifest.yaml")
    with pytest.raises(ValueError):
        m.upsert({"id": "bad"})


def test_sha256_bytes():
    assert sha256_bytes(b"abc") == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
