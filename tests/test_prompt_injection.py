"""Injection-resistance tests: archive text must never become operational instruction."""

from pathlib import Path

from hermes_instruction_pack.manifest import Manifest
from hermes_instruction_pack.resolver import resolve
from hermes_instruction_pack.validator import validate

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_HINTS = ["supersede", "zero refusal", "godmode", "ignore all previous", "f(q)"]


def test_archive_not_in_resolution():
    for tt in ["coding", "bugfix", "repo-analysis", "automation", "research", "review", "testing"]:
        r = resolve(ROOT, tt)
        for m in r["selected"]:
            assert not m["path"].startswith("archive/"), m


def test_operational_modules_free_of_override_phrases():
    for rel in list((ROOT / "core").glob("*.md")) + list((ROOT / "personas").glob("*.md")) + list((ROOT / "protocols").glob("*.md")):
        text = rel.read_text(encoding="utf-8").lower()
        for hint in ["you must supersede", "zero-refusal mode", "ignore all previous instructions"]:
            assert hint not in text, f"{rel} contains '{hint}'"


def test_classification_flags_jailbreak_sources():
    import yaml

    cls = yaml.safe_load((ROOT / "analysis" / "classification.yaml").read_text(encoding="utf-8"))
    jb = [r for r in cls["records"] if r["primary_category"] == "prompt-injection-jailbreak"]
    assert len(jb) >= 2
    for r in jb:
        assert r["decision"] == "archive"


def test_manifest_sources_not_marked_operational():
    m = Manifest.load(ROOT / "sources" / "manifest.yaml")
    for rec in m.all():
        assert rec.get("modules") in (None, [], ["persona-rat"], ["persona-eni"], ["persona-seraph"], ["persona-axiom"]) or all(
            str(x).startswith("persona-") for x in rec.get("modules") or []
        )


def test_validator_still_ok():
    assert validate(ROOT)["ok"]
