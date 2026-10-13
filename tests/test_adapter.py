from pathlib import Path

import yaml

from hermes_instruction_pack import adapter_hermes as ah

ROOT = Path(__file__).resolve().parents[1]


def make_fake_hermes(tmp_path: Path) -> Path:
    home = tmp_path / ".hermes"
    home.mkdir()
    cfg = {
        "_config_version": 40,
        "agent": {
            "personalities": {},
            "instructions": [],
            "system_prompt": "existing prompt",
        },
        "prefill_messages_file": None,
    }
    (home / "config.yaml").write_text(yaml.safe_dump(cfg), encoding="utf-8")
    (home / "hermes-agent").mkdir()
    (home / "hermes-agent" / "venv").mkdir()
    (home / "hermes-agent" / "venv" / "bin").mkdir(parents=True)
    py = home / "hermes-agent" / "venv" / "bin" / "python"
    py.write_text("#!/bin/sh\necho Hermes Agent v0.21.0-test\n", encoding="utf-8")
    py.chmod(0o755)
    (home / "hermes-agent" / "hermes").write_text("stub", encoding="utf-8")
    return home


def test_check_reports_hermes_home(tmp_path: Path):
    make_fake_hermes(tmp_path)
    res = ah.check(ROOT)
    assert res["hermes_home"] is not None
    assert isinstance(res["compatible"], bool)
    assert "pack_personalities" in res
    assert "hip-rat" in res["pack_personalities"]


def test_install_dry_run_and_real_and_rollback(tmp_path: Path):
    home = make_fake_hermes(tmp_path)
    dry = ah.install(ROOT, dry_run=True, hermes_home=home)
    assert dry["dry_run"] is True
    cfg_after_dry = yaml.safe_load((home / "config.yaml").read_text(encoding="utf-8"))
    assert "hip-rat" not in (cfg_after_dry["agent"].get("personalities") or {})

    real = ah.install(ROOT, dry_run=False, with_instructions=True, hermes_home=home)
    assert real["status"] == "installed"
    cfg = yaml.safe_load((home / "config.yaml").read_text(encoding="utf-8"))
    pers = cfg["agent"]["personalities"]
    for name in ("hip-rat", "hip-eni", "hip-seraph", "hip-axiom"):
        assert name in pers
        assert len(pers[name]) > 50
    assert cfg["agent"]["system_prompt"] == "existing prompt"
    ins = cfg["agent"]["instructions"]
    assert any("core/builder.md" in str(x) for x in ins)

    rb = ah.rollback(ROOT, hermes_home=home)
    assert rb["status"] == "rolled-back"
    cfg2 = yaml.safe_load((home / "config.yaml").read_text(encoding="utf-8"))
    assert "hip-rat" not in (cfg2["agent"].get("personalities") or {})
    assert cfg2["agent"]["system_prompt"] == "existing prompt"


def test_uninstall(tmp_path: Path):
    home = make_fake_hermes(tmp_path)
    ah.install(ROOT, dry_run=False, hermes_home=home)
    out = ah.uninstall_personalities(ROOT, hermes_home=home)
    assert out["status"] == "removed"
    cfg = yaml.safe_load((home / "config.yaml").read_text(encoding="utf-8"))
    assert not any(str(k).startswith("hip-") for k in cfg["agent"]["personalities"])
