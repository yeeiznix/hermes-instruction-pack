from pathlib import Path

from hermes_instruction_pack.importer import SourceImporter


def test_store_create_update_unchanged(tmp_path: Path):
    imp = SourceImporter(tmp_path)
    dest = imp.gists_dir / "g1" / "f.txt"
    assert imp._store(dest, b"hello") == "created"
    assert imp._store(dest, b"hello") == "unchanged"
    assert imp._store(dest, b"world!") == "updated"
    assert dest.read_bytes() == b"world!"
    backups = list(dest.parent.glob("f.txt.v*"))
    assert len(backups) == 1
    assert backups[0].read_bytes() == b"hello"


def test_failed_record_persisted(tmp_path: Path):
    imp = SourceImporter(tmp_path)
    rec = imp._failed_record(id="z", kind="gist", url="u", error="boom")
    assert rec["status"] == "failed"
    imp.finalize()
    m = imp.manifest
    assert m.get("z")["status"] == "failed"


def test_pinned_import_idempotent(tmp_path: Path, monkeypatch):
    class FakeResp:
        status_code = 200

        def __init__(self, content):
            self.content = content

        def raise_for_status(self):
            pass

    class FakeSession:
        def get(self, url, timeout=None):
            return FakeResp(b"payload-abc")

    import hermes_instruction_pack.importer as importer_mod

    monkeypatch.setattr(importer_mod, "_session", lambda: FakeSession())
    imp = SourceImporter(tmp_path)
    url = "https://gist.githubusercontent.com/u/1111111111111111111111111111111111111111/raw/aaa10d10426baff855e2c6e0aaced0ed753227a2/gistfile1.txt"
    rec = imp.import_gist_pinned(url)
    assert rec["status"] == "fetched"
    assert rec["commit"] == "aaa10d10426baff855e2c6e0aaced0ed753227a2"
    rec2 = imp.import_gist_pinned(url)
    assert rec2["store_action"] == "unchanged"
