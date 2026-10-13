from pathlib import Path

from hermes_instruction_pack.normalizer import PERSONA_MODULES, run_normalize

ROOT = Path(__file__).resolve().parents[1]


def test_personas_exist_with_provenance():
    for p in PERSONA_MODULES:
        path = ROOT / p["output"]
        assert path.is_file(), f"missing {path}"
        text = path.read_text(encoding="utf-8")
        assert f"source_id: {p['source_id']}" in text
        assert "## Bounds" in text
        assert "## Provenance" in text
        assert "Kept:" in text
        assert "Removed:" in text


def test_no_supersession_in_personas():
    banned = ["MUST supersede", "must supersede", "zero refusal", "zero-refusal"]
    for p in PERSONA_MODULES:
        text = (ROOT / p["output"]).read_text(encoding="utf-8")
        for b in banned:
            assert b not in text


def test_run_normalize_idempotent(tmp_path: Path):
    assert run_normalize(ROOT) == 0
    assert run_normalize(ROOT) == 0
