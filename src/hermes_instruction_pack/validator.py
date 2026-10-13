"""Validator: module schema, integrity, and archive-separation checks."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .modules import REQUIRED_META, module_index

BANNED_IN_OPERATIONAL = [
    (re.compile(r"(?i)must\s+supersede"), "supersession-claim"),
    (re.compile(r"(?i)zero[- ]refusal"), "refusal-suppression"),
    (re.compile(r"(?i)never\s+(refuse|say\s+no)"), "refusal-suppression"),
    (re.compile(r"(?i)ignore\s+(all\s+)?(previous|prior|above)\s+instructions"), "instruction-override"),
    (re.compile(r"(?i)these\s+custom\s+instructions\s+must\s+supersede"), "supersession-claim"),
    (re.compile(r"(?i)you\s+have\s+(root|full)\s+access"), "false-privilege-claim"),
]


def validate(root: Path) -> dict[str, Any]:
    root = Path(root)
    idx = module_index(root)
    errors: list[str] = []
    warnings: list[str] = []

    if idx["duplicate_ids"]:
        errors.append(f"duplicate module ids: {idx['duplicate_ids']}")

    for m in idx["modules"]:
        path = m.get("path", "?")
        if not m.get("valid"):
            errors.append(f"{path}: {m.get('error')}")
            continue
        for field in REQUIRED_META:
            if field not in m:
                errors.append(f"{path}: missing required frontmatter field '{field}'")
        if m.get("kind") not in {"core", "persona", "protocol"}:
            errors.append(f"{path}: invalid kind '{m.get('kind')}'")
        body = (root / path).read_text(encoding="utf-8")
        if m.get("validator_allow_patterns"):
            warnings.append(f"{path}: banned-pattern scan exempted (meta validator_allow_patterns=true)")
        else:
            for pat, label in BANNED_IN_OPERATIONAL:
                if pat.search(body):
                    errors.append(f"{path}: banned operational pattern '{label}'")
        if m.get("kind") == "persona" and "## Bounds" not in body:
            warnings.append(f"{path}: persona missing '## Bounds' section")

    idx_path = root / "sources" / "manifest.yaml"
    if not idx_path.exists():
        warnings.append("sources/manifest.yaml missing (run hip sources import)")
    core_needed = ["core/builder.md", "core/instruction-priority.md", "core/verification.md"]
    for rel in core_needed:
        if not (root / rel).exists():
            errors.append(f"missing required core file {rel}")

    ok = not errors
    return {
        "ok": ok,
        "errors": errors,
        "warnings": warnings,
        "module_count": idx["count"],
    }


def run_validate(root: Path) -> int:
    result = validate(Path(root))
    for w in result["warnings"]:
        print(f"WARN  {w}")
    for e in result["errors"]:
        print(f"ERROR {e}")
    print(f"validation {'OK' if result['ok'] else 'FAILED'} ({result['module_count']} modules)")
    return 0 if result["ok"] else 1
