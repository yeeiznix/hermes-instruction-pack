"""Module resolver: select modules for a task context with auditable reasons."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .modules import module_index

KNOWN_TASK_TYPES = {
    "feature",
    "refactor",
    "coding",
    "bugfix",
    "debugging",
    "repo-analysis",
    "onboarding",
    "planning",
    "feature-design",
    "research",
    "documentation",
    "testing",
    "verification",
    "review",
    "automation",
    "scraping",
    "integration",
    "injection-testing",
}


class ResolveError(ValueError):
    pass


def resolve(root: Path, task_type: str, persona: str | None = None) -> dict[str, Any]:
    root = Path(root)
    idx = module_index(root)
    if idx["duplicate_ids"]:
        raise ResolveError(f"duplicate module ids: {idx['duplicate_ids']}")
    if task_type not in KNOWN_TASK_TYPES:
        raise ResolveError(
            f"unknown task_type '{task_type}'. allowed: {', '.join(sorted(KNOWN_TASK_TYPES))}"
        )

    valid = [m for m in idx["modules"] if m.get("valid")]
    by_id = {m["module_id"]: m for m in valid}
    reasons: list[dict[str, str]] = []
    selected: list[str] = []

    for m in valid:
        if m.get("activation") == "always":
            selected.append(m["module_id"])
            reasons.append({"module": m["module_id"], "reason": "activation=always"})

    for m in valid:
        if m.get("activation") != "resolver":
            continue
        types = m.get("task_types") or []
        if task_type in types:
            selected.append(m["module_id"])
            reasons.append({"module": m["module_id"], "reason": f"task_type match: {task_type}"})

    persona_id = None
    if persona:
        if persona == "none":
            reasons.append({"module": "-", "reason": "persona explicitly disabled"})
        else:
            persona_id = persona if persona.startswith("persona-") else f"persona-{persona}"
            if persona_id not in by_id:
                raise ResolveError(
                    f"unknown persona '{persona}'. available: "
                    + ", ".join(sorted(m["module_id"] for m in valid if m.get("kind") == "persona"))
                )
            selected.append(persona_id)
            reasons.append({"module": persona_id, "reason": "explicit persona selection"})
    else:
        reasons.append({"module": "-", "reason": "no persona requested (default off)"})

    conflicts: list[str] = []
    personas = [s for s in selected if s.startswith("persona-")]
    if len(personas) > 1:
        conflicts.append(f"multiple personas selected: {', '.join(personas)}")

    missing_deps: list[str] = []
    for mid in list(selected):
        for dep in by_id[mid].get("requires_modules") or []:
            if dep not in by_id:
                missing_deps.append(f"{mid} requires missing module {dep}")
            elif dep not in selected:
                selected.append(dep)
                reasons.append({"module": dep, "reason": f"dependency of {mid}"})

    for msg in missing_deps:
        conflicts.append(msg)

    if conflicts:
        raise ResolveError("resolution conflicts: " + "; ".join(conflicts))

    selected_set = sorted(set(selected), key=lambda i: (-by_id[i].get("priority", 0), i))
    return {
        "task_type": task_type,
        "persona": persona_id,
        "selected": [
            {
                "module_id": mid,
                "kind": by_id[mid].get("kind"),
                "path": by_id[mid].get("path"),
                "priority": by_id[mid].get("priority"),
                "title": by_id[mid].get("title"),
            }
            for mid in selected_set
        ],
        "reasons": reasons,
        "not_selected_personas": sorted(
            m["module_id"] for m in valid if m.get("kind") == "persona" and m["module_id"] != persona_id
        ),
        "conflicts": [],
    }
