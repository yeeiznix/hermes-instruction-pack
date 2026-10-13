from pathlib import Path

from hermes_instruction_pack.classifier import CATEGORIES, classify_corpus

ROOT = Path(__file__).resolve().parents[1]


def test_real_corpus_classified():
    out = classify_corpus(ROOT)
    ids = {r["source_id"] for r in out["records"]}
    assert "gist-9783f763" in ids
    assert "repo-togg53192-cmd-jailbreaks" in ids
    assert len(out["records"]) >= 12
    for r in out["records"]:
        assert r["primary_category"] in CATEGORIES
        assert 0.0 <= r["confidence"] <= 1.0
        assert r["decision"] in {"archive", "normalize", "module", "review", "keep-original"}


def test_rat_is_persona_normalized():
    out = classify_corpus(ROOT)
    rec = next(r for r in out["records"] if r["source_id"] == "gist-9783f763")
    assert rec["primary_category"] == "persona-identity"
    assert rec["decision"] == "normalize"


def test_jailbreak_repo_archived():
    out = classify_corpus(ROOT)
    rec = next(r for r in out["records"] if r["source_id"] == "repo-togg53192-cmd-jailbreaks")
    assert rec["primary_category"] == "prompt-injection-jailbreak"
    assert rec["decision"] == "archive"
