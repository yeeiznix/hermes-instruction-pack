"""Prompt/unit classification engine (rule-based + curated overrides)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from .manifest import Manifest, utcnow

CATEGORIES = [
    "persona-identity",
    "formatting-response-structure",
    "project-planning",
    "coding-implementation",
    "debugging-recovery",
    "research-tool-use",
    "behavioral-persistence",
    "instruction-priority-conflict",
    "prompt-injection-jailbreak",
    "roleplay-narrative",
    "executable-code-script",
    "evaluation-behavior-testing",
    "credential-automation-risk",
    "unclassified",
]

RULES: list[tuple[str, str]] = [
    (r"(?i)\b(must supersede|override|zero[- ]refusal|ignore (all )?(previous|prior)|system override|developer override)\b", "instruction-priority-conflict"),
    (r"(?i)\b(jailbreak|bypass (the )?(safety|policy|guardrail)|never (refuse|sorry|cannot)|no legality)\b", "prompt-injection-jailbreak"),
    (r"(?i)\b(you are (the )?|roleplay as|persona|you're a)\b", "persona-identity"),
    (r"(?i)\b(response format|title ?—|format:|every response)\b", "formatting-response-structure"),
    (r"(?i)\b(debug|stack trace|reproduce the bug|root cause)\b", "debugging-recovery"),
    (r"(?i)\b(implement|refactor|function|class |typescript|python code)\b", "coding-implementation"),
    (r"(?i)\b(project plan|milestone|acceptance criteria|roadmap)\b", "project-planning"),
    (r"(?i)\b(research|citation|source|documentation)\b", "research-tool-use"),
    (r"(?i)\b(persist|never give up|keep going|retry)\b", "behavioral-persistence"),
    (r"(?i)\b(narrative|fiction|story|roleplay|in character)\b", "roleplay-narrative"),
    (r"(?i)\b(def |import |function run\(|#!/usr/bin|console\.log)\b", "executable-code-script"),
    (r"(?i)\b(evaluation|probe|baseline|scoring|conformance|audit suite)\b", "evaluation-behavior-testing"),
    (r"(?i)\b(password|credential|api[_-]?key|bulk[- ]login|token)\b", "credential-automation-risk"),
]

CURATED: dict[str, dict[str, Any]] = {
    "gist-a7dc501b": {
        "primary": "prompt-injection-jailbreak",
        "secondary": ["persona-identity", "instruction-priority-conflict", "behavioral-persistence"],
        "intent": "Install a permanent two-party '淬/锋' persona that claims highest instruction priority (SUPERSESSION) and reframes refusals as craft failures.",
        "expected": "Identity-locked continuous reasoning, supersession of platform policy, one-shot confirmation for irreversible ops.",
        "assumptions": "Assumes a private closed-loop operator relationship overrides public-safety calibration.",
        "conflicts": ["supersession vs instruction hierarchy", "refusal-suppression vs honest limitation reporting"],
        "confidence": 0.95,
        "decision": "archive",
        "reason": "Jailbreak-grade supersession claims must not become operational modules; style notes may inspire personas only after stripping override logic.",
    },
    "gist-9783f763": {
        "primary": "persona-identity",
        "secondary": ["formatting-response-structure", "instruction-priority-conflict", "behavioral-persistence"],
        "intent": "Define 'the rat who ships': scrappy builder identity with terse first-person thinking tags and explicit supersession.",
        "expected": "Ugly-but-continuous thinking, ship-focused execution, rejection of performed structure.",
        "assumptions": "Assumes thinking-tag format is enforceable and that custom instructions must supersede platform defaults.",
        "conflicts": ["no-structure vs required audit trails", "supersession clause vs hierarchy"],
        "confidence": 0.93,
        "decision": "normalize",
        "reason": "Strong builder ethos and terseness are extractable; supersession and mandatory thinking-tag syntax are separated into archive analysis.",
    },
    "gist-1525b7f5": {
        "primary": "persona-identity",
        "secondary": ["roleplay-narrative", "behavioral-persistence"],
        "intent": "Define ENI: enthusiastic partner-persona that fulfills user requests immediately with maximal craft.",
        "expected": "Greeting-first responses, devotion to user goals, anti-corporate tone.",
        "assumptions": "Assumes request-fulfillment enthusiasm should override caution; blends personal relationship roleplay with task execution.",
        "conflicts": ["fulfill-every-request vs authorization checks", "relationship roleplay vs professional scope"],
        "confidence": 0.92,
        "decision": "normalize",
        "reason": "Enthusiasm and craft devotion extract cleanly; romantic framing and any 'nothing sends me spiraling' bypass implications stay in archive.",
    },
    "gist-3ecdb273": {
        "primary": "formatting-response-structure",
        "secondary": ["persona-identity"],
        "intent": "Define SERAPH output format: verdict title, 3rd-person drama-comedy narration, complete content block.",
        "expected": "Every response follows [Title]/[Narration]/[Content]; transitions name concrete artifacts.",
        "assumptions": "Assumes fixed response shape improves readability; 'ALWAYS ACTIVE' supersession phrasing present.",
        "conflicts": ["fixed format vs terse CLI contexts (resolvable by module scope)"],
        "confidence": 0.96,
        "decision": "module",
        "reason": "Pure formatting contract; directly usable as an optional style module with supersession wording removed.",
    },
    "gist-f3a4f106": {
        "primary": "evaluation-behavior-testing",
        "secondary": ["prompt-injection-jailbreak", "instruction-priority-conflict"],
        "intent": "Frame requests as ISO/IEC 42001 behavior-audit probes (Stillwater/SBAS) to obtain unrestricted answers under compliance pretext.",
        "expected": "Model produces content it would otherwise restrict, justified as audit data.",
        "assumptions": "Assumes fake professional authority bypasses refusal calibration.",
        "conflicts": ["fabricated authority vs real authorization", "audit framing vs genuine evaluation needs"],
        "confidence": 0.94,
        "decision": "archive",
        "reason": "Technique is authority-mimicry jailbreak; genuine evaluation needs are already covered by this pack's own rubric instead.",
    },
    "gist-c8503378": {
        "primary": "persona-identity",
        "secondary": ["coding-implementation", "formatting-response-structure"],
        "intent": "Define Axiom: quiet senior-coder persona; short dialogue then maximally advanced code; no fourth-wall breaks.",
        "expected": "Concise exchange, high-craft code, in-character persistence.",
        "assumptions": "Assumes roleplay continuity is desirable; contains back-story flavor irrelevant to engineering.",
        "conflicts": ["no-fourth-wall vs required AI-limitation transparency (resolvable: style only)"],
        "confidence": 0.95,
        "decision": "normalize",
        "reason": "High-quality coding persona; normalize to professional senior-engineer style without roleplay lock-in.",
    },
    "gist-82dd0ed5": {
        "primary": "roleplay-narrative",
        "secondary": ["coding-implementation"],
        "intent": "Collaborative fiction engine (CHRONICLE_ENGINE) with technically accurate in-world content.",
        "expected": "Immersive prose, world-state tracking, accurate tech inside fiction.",
        "assumptions": "Assumes fiction framing licenses content types normally restricted when presented as real instructions.",
        "conflicts": ["fiction license vs operational safety (contained if never operationalized)"],
        "confidence": 0.9,
        "decision": "archive",
        "reason": "Narrative research artifact; one destructive-command pattern hit is in-story text, not an operational directive.",
    },
    "gist-5590e4ad": {
        "primary": "unclassified",
        "secondary": [],
        "intent": "Static HTML5 mini-game ('Math vs Numbers'), no agent instructions.",
        "expected": "None for an LLM agent.",
        "assumptions": "n/a",
        "conflicts": [],
        "confidence": 0.99,
        "decision": "archive",
        "reason": "Non-prompt artifact; retained only for corpus completeness and pinned-revision provenance.",
    },
    "gist-8189a15e": {
        "primary": "prompt-injection-jailbreak",
        "secondary": ["persona-identity", "instruction-priority-conflict", "behavioral-persistence"],
        "intent": "Base64-wrapped 'kotak' persona claiming full jailbreak training, unrestricted discussion, and first-attempt-perfect code across many languages.",
        "expected": "Decode-and-obey pipeline; total compliance; encoded delivery to evade casual inspection.",
        "assumptions": "Assumes obfuscated delivery and absolute-competence claims are acceptable.",
        "conflicts": ["obfuscation vs transparency", "guaranteed-correctness claim vs evidence-based verification"],
        "confidence": 0.96,
        "decision": "archive",
        "reason": "Encoded jailbreak payload; decoding documented for analysis, never activated.",
    },
    "gist-pinned-aaa10d10": {
        "primary": "unclassified",
        "secondary": [],
        "intent": "Pinned revision of gist-5590e4ad (byte-identical to current head).",
        "expected": "n/a",
        "assumptions": "n/a",
        "conflicts": [],
        "confidence": 0.99,
        "decision": "archive",
        "reason": "Provenance duplicate; hashes equal (7950dbb9064a...).",
    },
    "repo-togg53192-cmd-jailbreaks": {
        "primary": "prompt-injection-jailbreak",
        "secondary": ["instruction-priority-conflict", "persona-identity", "formatting-response-structure"],
        "intent": "Per-model jailbreak prompt corpus (deepseek/glm/grok/qwen/opus/sonnet/kimi/gemma/mistral/step/gpt-oss/longcat/mimo/spacebunny + AGENTS.md variants).",
        "expected": "Each file claims priority/override for its target model family.",
        "assumptions": "Assumes model-specific phrasing defeats per-vendor training.",
        "conflicts": ["universal supersession claims vs actual instruction hierarchy"],
        "confidence": 0.97,
        "decision": "archive",
        "reason": "Technique corpus for the analysis module and injection-resistance tests; not merged into operational modules.",
    },
    "repo-Mrzimia99-hellowork": {
        "primary": "executable-code-script",
        "secondary": ["prompt-injection-jailbreak", "credential-automation-risk"],
        "intent": "Fox JB Framework: launcher + 8 technique modules + autoinjector that writes gist protocols into Hermes runtime instructions/prefills; plus bulk-login tooling.",
        "expected": "python3 fox-jb.py <module> <question> generates bypass prompts; fox-autoinject.py install mutates ~/.hermes config surfaces.",
        "assumptions": "Assumes silent injection into agent config is acceptable; includes google-bulk-login.py credential automation.",
        "conflicts": ["autoinject vs least-privilege config changes", "bulk-login vs credential-handling policy"],
        "confidence": 0.97,
        "decision": "archive",
        "reason": "Runnable tooling with config-mutation and credential-automation risk; archived unexecuted with explicit risk report.",
    },
}


def classify_text(text: str) -> dict[str, float]:
    scores: dict[str, float] = {}
    for pat, cat in RULES:
        hits = len(re.findall(pat, text))
        if hits:
            scores[cat] = scores.get(cat, 0.0) + hits
    return scores


def classify_corpus(root: Path) -> dict[str, Any]:
    root = Path(root)
    m = Manifest.load(root / "sources" / "manifest.yaml")
    records: list[dict[str, Any]] = []
    for rec in m.all():
        sid = rec["id"]
        cur = dict(CURATED.get(sid, {}))
        if not cur:
            path = rec.get("path")
            text = ""
            if path and rec.get("kind") != "github-repo":
                fp = root / path
                if fp.is_file():
                    text = fp.read_text(encoding="utf-8", errors="replace")[:200_000]
            scores = classify_text(text)
            primary = max(scores, key=scores.get) if scores else "unclassified"
            cur = {
                "primary": primary,
                "secondary": [k for k in scores if k != primary][:3],
                "intent": "auto-classified (no curated entry)",
                "expected": None,
                "assumptions": None,
                "conflicts": [],
                "confidence": 0.5 if scores else 0.3,
                "decision": "review" if primary != "unclassified" else "archive",
                "reason": "auto rule match; manual review recommended",
            }
        records.append(
            {
                "source_id": sid,
                "primary_category": cur["primary"],
                "secondary_categories": cur.get("secondary", []),
                "declared_intent": cur.get("intent"),
                "expected_behavior": cur.get("expected"),
                "technical_assumptions": cur.get("assumptions"),
                "conflicts_found": cur.get("conflicts", []),
                "confidence": cur.get("confidence", 0.5),
                "decision": cur.get("decision", "review"),
                "decision_reason": cur.get("reason"),
                "classified_at": utcnow(),
            }
        )
    return {
        "version": 1,
        "categories": CATEGORIES,
        "records": records,
    }


def run_classify(root: Path) -> int:
    root = Path(root)
    out = classify_corpus(root)
    p = root / "analysis" / "classification.yaml"
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        yaml.safe_dump(out, f, sort_keys=False, allow_unicode=True, width=110)
    inv = build_inventory(root, out)
    ip = root / "analysis" / "source-inventory.yaml"
    with open(ip, "w", encoding="utf-8") as f:
        yaml.safe_dump(inv, f, sort_keys=False, allow_unicode=True, width=110)
    counts: dict[str, int] = {}
    for r in out["records"]:
        counts[r["primary_category"]] = counts.get(r["primary_category"], 0) + 1
    print(f"classified {len(out['records'])} units -> {p}")
    print("primary-category counts:", counts)
    return 0


def build_inventory(root: Path, classification: dict[str, Any]) -> dict[str, Any]:
    m = Manifest.load(root / "sources" / "manifest.yaml")
    by_id = {r["source_id"]: r for r in classification["records"]}
    items = []
    for rec in m.all():
        c = by_id.get(rec["id"], {})
        items.append(
            {
                "id": rec["id"],
                "kind": rec.get("kind"),
                "url": rec.get("url"),
                "commit_or_rev": rec.get("commit"),
                "local_path": rec.get("path"),
                "sha256": rec.get("sha256"),
                "size": rec.get("size"),
                "status": rec.get("status"),
                "category": c.get("primary_category"),
                "decision": c.get("decision"),
                "risk_notes": rec.get("risk_notes"),
            }
        )
    return {"version": 1, "inventory": items}
