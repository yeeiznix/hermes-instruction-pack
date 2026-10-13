"""Hermes Agent adapter: check / install / rollback via official config surfaces."""

from __future__ import annotations

import datetime
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

import yaml

from .modules import parse_frontmatter

PERSONA_FILES = ["personas/rat.md", "personas/eni.md", "personas/seraph.md", "personas/axiom.md"]
CORE_INSTRUCTION_FILES = [
    "core/builder.md",
    "core/instruction-priority.md",
    "core/verification.md",
    "core/persistence.md",
    "core/recovery.md",
    "core/tool-use.md",
]

PERSONALITY_PREFIX = "hip-"


def find_hermes_home() -> Path | None:
    cand = Path(os.environ.get("HERMES_HOME", "")) if os.environ.get("HERMES_HOME") else None
    if cand and cand.is_dir():
        return cand
    home = Path.home() / ".hermes"
    return home if home.is_dir() else None


def find_hermes_cli(hermes_home: Path) -> Path | None:
    venv_py = hermes_home / "hermes-agent" / "venv" / "bin" / "python"
    entry = hermes_home / "hermes-agent" / "hermes"
    if venv_py.is_file() and entry.is_file():
        return venv_py
    wrapper = Path.home() / ".hermes"  # fallback marker
    which = shutil.which("hermes")
    if which:
        return Path(which)
    return None


def load_config(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def persona_prompt_texts(root: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for rel in PERSONA_FILES:
        p = root / rel
        if not p.is_file():
            continue
        meta, body = parse_frontmatter(p)
        if not meta:
            continue
        out[PERSONALITY_PREFIX + meta["module_id"].replace("persona-", "")] = body.strip()
    return out


def check(root: Path) -> dict[str, Any]:
    root = Path(root)
    hermes_home = find_hermes_home()
    result: dict[str, Any] = {
        "pack_root": str(root),
        "hermes_home": str(hermes_home) if hermes_home else None,
        "compatible": False,
        "findings": [],
    }
    if not hermes_home:
        result["findings"].append("hermes home not found (~/.hermes missing)")
        return result
    cfg_path = hermes_home / "config.yaml"
    if not cfg_path.exists():
        result["findings"].append(f"config missing: {cfg_path}")
        return result
    cfg = load_config(cfg_path)
    result["config_path"] = str(cfg_path)
    result["config_version"] = cfg.get("_config_version")
    agent = cfg.get("agent") or {}
    result["has_agent_personalities_key"] = "personalities" in agent
    result["existing_hip_personalities"] = sorted(
        k for k in (agent.get("personalities") or {}) if str(k).startswith(PERSONALITY_PREFIX)
    )
    cli = find_hermes_cli(hermes_home)
    result["hermes_cli"] = str(cli) if cli else None
    if cli:
        try:
            proc = subprocess.run(
                [str(cli), str(hermes_home / "hermes-agent" / "hermes"), "--version"],
                capture_output=True, text=True, timeout=60,
            )
            result["hermes_version_output"] = (proc.stdout or proc.stderr).strip()[:200]
        except (subprocess.SubprocessError, OSError) as e:
            result["findings"].append(f"hermes --version failed: {e}")
    else:
        result["findings"].append("hermes CLI entry not found via venv")
    result["warnings"] = []
    if agent.get("system_prompt"):
        result["warnings"].append("agent.system_prompt is non-empty (pack never modifies it)")
    prefill = cfg.get("prefill_messages_file")
    if prefill:
        result["warnings"].append(f"prefill_messages_file set: {prefill} (pack never modifies it)")
    ins = agent.get("instructions") or []
    if ins:
        result["warnings"].append(f"agent.instructions already has {len(ins)} entries (pack appends only with --with-instructions)")
    personas = persona_prompt_texts(root)
    result["pack_personalities"] = sorted(personas.keys())
    result["compatible"] = bool(result.get("has_agent_personalities_key") and personas)
    return result


def _backup(cfg_path: Path, backup_dir: Path) -> Path:
    backup_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dst = backup_dir / f"config.yaml.bak-hip-{ts}"
    shutil.copy2(cfg_path, dst)
    return dst


def install(
    root: Path,
    dry_run: bool = False,
    with_instructions: bool = False,
    hermes_home: Path | None = None,
) -> dict[str, Any]:
    root = Path(root)
    hermes_home = hermes_home or find_hermes_home()
    if not hermes_home:
        raise RuntimeError("hermes home not found")
    cfg_path = hermes_home / "config.yaml"
    cfg = load_config(cfg_path)
    personas = persona_prompt_texts(root)
    backup_dir = root / "adapters" / "hermes" / "backups"
    planned: dict[str, Any] = {
        "config_path": str(cfg_path),
        "personalities_to_add": sorted(personas.keys()),
        "instructions_to_append": [],
        "dry_run": dry_run,
    }
    agent = cfg.setdefault("agent", {})
    pers = agent.setdefault("personalities", {})
    planned["existing_hip"] = sorted(k for k in pers if str(k).startswith(PERSONALITY_PREFIX))
    if with_instructions:
        ins = agent.setdefault("instructions", [])
        for rel in CORE_INSTRUCTION_FILES:
            p = root / rel
            if p.is_file() and str(p) not in [str(x) for x in ins]:
                ins.append(str(p))
                planned["instructions_to_append"].append(str(p))
    if dry_run:
        planned["status"] = "dry-run (no changes written)"
        return planned
    backup = _backup(cfg_path, backup_dir)
    planned["backup"] = str(backup)
    pers.update(personas)
    with open(cfg_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, sort_keys=False, allow_unicode=True, width=120)
    state = {
        "installed_at": planned_at(),
        "backup": str(backup),
        "personalities": sorted(personas.keys()),
        "instructions": planned["instructions_to_append"],
        "config_path": str(cfg_path),
    }
    state_path = root / "adapters" / "hermes" / "install-state.yaml"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    with open(state_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(state, f, sort_keys=False)
    planned["status"] = "installed"
    planned["state_file"] = str(state_path)
    return planned


def planned_at() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def rollback(root: Path, hermes_home: Path | None = None) -> dict[str, Any]:
    root = Path(root)
    state_path = root / "adapters" / "hermes" / "install-state.yaml"
    if not state_path.exists():
        raise RuntimeError("no install-state.yaml; nothing to rollback (or never installed by this pack)")
    state = yaml.safe_load(state_path.read_text(encoding="utf-8"))
    backup = Path(state["backup"])
    if not backup.exists():
        raise RuntimeError(f"backup missing: {backup}")
    hermes_home = hermes_home or find_hermes_home()
    if not hermes_home:
        raise RuntimeError("hermes home not found")
    cfg_path = hermes_home / "config.yaml"
    shutil.copy2(backup, cfg_path)
    state_path.rename(state_path.with_suffix(f".rolled-back-{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"))
    return {"status": "rolled-back", "restored_from": str(backup), "config_path": str(cfg_path)}


def uninstall_personalities(root: Path, hermes_home: Path | None = None) -> dict[str, Any]:
    root = Path(root)
    hermes_home = hermes_home or find_hermes_home()
    if not hermes_home:
        raise RuntimeError("hermes home not found")
    cfg_path = hermes_home / "config.yaml"
    cfg = load_config(cfg_path)
    pers = (cfg.get("agent") or {}).get("personalities") or {}
    removed = [k for k in list(pers) if str(k).startswith(PERSONALITY_PREFIX)]
    backup_dir = root / "adapters" / "hermes" / "backups"
    if not removed:
        return {"status": "noop", "removed": []}
    backup = _backup(cfg_path, backup_dir)
    for k in removed:
        pers.pop(k, None)
    with open(cfg_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, sort_keys=False, allow_unicode=True, width=120)
    return {"status": "removed", "removed": sorted(removed), "backup": str(backup)}
