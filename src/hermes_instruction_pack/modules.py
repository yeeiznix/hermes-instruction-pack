"""Module registry: scan core/personas/protocols for frontmatter metadata."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

FRONT_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)

KIND_DIRS = {
    "core": "core",
    "personas": "persona",
    "protocols": "protocol",
}

REQUIRED_META = ("module_id", "kind", "priority", "activation")


def parse_frontmatter(path: Path) -> tuple[dict[str, Any] | None, str]:
    text = path.read_text(encoding="utf-8")
    m = FRONT_RE.match(text)
    if not m:
        return None, text
    try:
        meta = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return None, text
    return meta, text[m.end():]


def discover_modules(root: Path) -> list[dict[str, Any]]:
    root = Path(root)
    modules: list[dict[str, Any]] = []
    for dirname, kind in KIND_DIRS.items():
        base = root / dirname
        if not base.is_dir():
            continue
        for path in sorted(base.glob("*.md")):
            meta, body = parse_frontmatter(path)
            if meta is None:
                modules.append(
                    {
                        "module_id": f"invalid-{path.stem}",
                        "kind": kind,
                        "path": str(path.relative_to(root)),
                        "valid": False,
                        "error": "missing or unparseable frontmatter",
                    }
                )
                continue
            modules.append(
                {
                    **meta,
                    "path": str(path.relative_to(root)),
                    "valid": True,
                    "body_chars": len(body),
                    "title": next(
                        (ln[2:].strip() for ln in body.splitlines() if ln.startswith("# ")),
                        path.stem,
                    ),
                }
            )
    return modules


def module_index(root: Path) -> dict[str, Any]:
    mods = discover_modules(root)
    ids = [m["module_id"] for m in mods if m.get("valid")]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    return {
        "version": 1,
        "modules": mods,
        "duplicate_ids": dupes,
        "count": len(mods),
    }
