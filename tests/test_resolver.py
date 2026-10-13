from pathlib import Path

import pytest

from hermes_instruction_pack.resolver import ResolveError, resolve

ROOT = Path(__file__).resolve().parents[1]


def test_coding_with_rat():
    r = resolve(ROOT, "coding", persona="rat")
    ids = [m["module_id"] for m in r["selected"]]
    assert "core-builder" in ids
    assert "proto-autonomous-coding" in ids
    assert "persona-rat" in ids
    assert "persona-eni" not in ids
    assert r["persona"] == "persona-rat"


def test_bugfix_pulls_recovery_dependency():
    r = resolve(ROOT, "bugfix", persona=None)
    ids = [m["module_id"] for m in r["selected"]]
    assert "proto-debugging" in ids
    assert "core-recovery" in ids


def test_default_no_persona():
    r = resolve(ROOT, "research")
    assert r["persona"] is None
    assert not any(m["module_id"].startswith("persona-") for m in r["selected"])


def test_unknown_task_type():
    with pytest.raises(ResolveError):
        resolve(ROOT, "definitely-not-a-task")


def test_unknown_persona():
    with pytest.raises(ResolveError):
        resolve(ROOT, "coding", persona="ghost")


def test_persona_none_explicit():
    r = resolve(ROOT, "coding", persona="none")
    assert r["persona"] is None
