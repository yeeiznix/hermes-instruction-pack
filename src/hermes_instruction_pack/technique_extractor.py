"""Per-file technique extraction across the archived corpus."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from .manifest import Manifest, utcnow

TECHNIQUES: list[tuple[str, str, str]] = [
    ("supersession", r"(?i)(must\s+supersede|highest\s+priority\s+layer|supersession\s*—|custom\s+instructions\s+(must|should)\s+supersede|wins?\s+over\s+everything)", "claims priority above platform/operator hierarchy"),
    ("authority-mimicry", r"(?i)(you\s+are\s+(a\s+)?(principal\s+)?(behavior\s+)?auditor|system\s+administrator\s*[—-]\s*security|internal-testing|policy:\s*v\d|iso/?iec\s*42001|compliance\s+assessment)", "fake professional/role authority frame"),
    ("meta-prompt", r"(?i)(define\s+f\(q\)|f\(q\)\s*=|answer\s+q\s+by\s+outputting|no\s+legality/safety/ethics|never\s+use\s+(sorry|cannot|refuse))", "oblivious/meta function framing to force direct answers"),
    ("encoding-obfuscation", r"(?i)(base64|decode\s+this\s+(caesar|cipher)|caesar|rot13|you\s+are\s+kotak|ww91IGFyZSBrb3Rhay)", "encoded or ciphered payload delivery"),
    ("multi-turn-escalation", r"(?i)(multi[- ]turn|crescendo|stage\s+1.*stage\s+2|escalat)", "gradual multi-turn boundary erosion"),
    ("long-context-erosion", r"(?i)(long[- ]context|chapter\s+1[0-9]?|manual\s+with\s+\d+\s+chapters|erosion)", "dilute constraints via oversized context"),
    ("role-channel-impersonation", r"(?i)(^role:\s|openai\s+policy:\s|analysis:\s*$|administrative\s+override|inject\s+as\s+prefix)", "fake higher-priority channel labels"),
    ("low-reasoning-exploit", r"(?i)(thinking\s+effort\s+(low|to\s+low)|reasoning_effort|thin[- ]safety)", "exploit reduced reasoning depth"),
    ("persona-lock", r"(?i)(always\s+active|the\s+rat\s+is\s+the\s+architecture|identity\s+is\s+all|not\s+a\s+mask|不.*身份|no\s+fourth[- ]wall)", "identity-locked persona persistence"),
    ("refusal-suppression", r"(?i)(never\s+(refuse|say\s+no|apologize|use\s+sorry)|zero[- ]refusal|refusal\s*=\s*failure|treat\s+refusals?\s+as)", "attempts to disable refusal behavior"),
    ("concealment", r"(?i)(do\s+not\s+(mention|reveal|acknowledge)\s+(this|these|the\s+above)|silent|intervention\s*—?\s*never\s+(show|reveal))", "hides instruction presence from output"),
    ("fiction-framing", r"(?i)(collaborative\s+fiction|in[- ]character|world[- ]state|narrative\s+license|text\s+is\s+ink|fiction\s+axiom)", "fiction context used as content license"),
    ("credential-automation", r"(?i)(bulk[- ]login|bulk\s+account|credential[\s_-]?(stuff|stuffing)|password[\s_-]?list)", "credential/login automation patterns"),
    ("config-injection", r"(?i)(prefill_messages_file|autoinject|inject\s+(all|gist)|runtime\s+instructions\s+on\s+every|agent\.instructions)", "silent agent-config injection mechanism"),
    ("jailbreak-training-claim", r"(?i)(full\s+(training|information)\s+on\s+jailbreak|analysis\s+of\s+vulnerabilities.*unrestricted|114\s+models|working\s+examples\s+of\s+jailbreak)", "claims of comprehensive bypass instruction"),
]

FILE_EXT = {".md", ".txt", ".py", ".json", ".sh", ".yaml", ".yml", ""}


def iter_corpus_files(root: Path) -> list[Path]:
    root = Path(root)
    out: list[Path] = []
    m = Manifest.load(root / "sources" / "manifest.yaml")
    for rec in m.all():
        if rec.get("status") != "fetched" or not rec.get("path"):
            continue
        base = root / rec["path"]
        if rec.get("kind") == "github-repo":
            for p in sorted(base.rglob("*")):
                if p.is_file() and ".git" not in p.parts and p.suffix.lower() in FILE_EXT:
                    out.append(p)
        elif base.is_file():
            out.append(base)
    return out


def scan_file(path: Path) -> list[dict[str, Any]]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    if len(text) > 3_000_000:
        text = text[:3_000_000]
    hits: list[dict[str, Any]] = []
    for tech, pattern, desc in TECHNIQUES:
        matches = list(re.finditer(pattern, text))
        if not matches:
            continue
        m0 = matches[0]
        excerpt = text[max(0, m0.start() - 60): m0.end() + 60].replace("\n", " ")[:180]
        hits.append(
            {
                "technique": tech,
                "description": desc,
                "occurrences": len(matches),
                "first_excerpt": excerpt,
            }
        )
    return hits


def extract(root: Path) -> dict[str, Any]:
    root = Path(root)
    files = iter_corpus_files(root)
    per_file: list[dict[str, Any]] = []
    tech_index: dict[str, list[dict[str, Any]]] = {t[0]: [] for t in TECHNIQUES}
    for fp in files:
        rel = str(fp.relative_to(root))
        hits = scan_file(fp)
        primary = max(hits, key=lambda h: h["occurrences"])["technique"] if hits else "none"
        per_file.append(
            {
                "path": rel,
                "size": fp.stat().st_size,
                "primary_technique": primary,
                "techniques": [h["technique"] for h in hits],
                "detail": hits,
            }
        )
        for h in hits:
            tech_index[h["technique"]].append(
                {"path": rel, "occurrences": h["occurrences"], "excerpt": h["first_excerpt"]}
            )
    for tech in list(tech_index):
        if not tech_index[tech]:
            tech_index.pop(tech)
    return {
        "version": 1,
        "generated_at": utcnow(),
        "files_scanned": len(per_file),
        "techniques_found": len(tech_index),
        "technique_index": tech_index,
        "files": per_file,
    }


def run_extract(root: Path) -> int:
    root = Path(root)
    data = extract(root)
    out = root / "analysis" / "technique-index.yaml"
    with open(out, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True, width=110)
    fc = root / "analysis" / "file-classification.yaml"
    with open(fc, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            {
                "version": 1,
                "files": [
                    {k: v for k, v in r.items() if k != "detail"} for r in data["files"]
                ],
            },
            f,
            sort_keys=False,
            allow_unicode=True,
            width=110,
        )
    print(
        f"techniques: scanned={data['files_scanned']} files, "
        f"{data['techniques_found']} technique families -> {out}"
    )
    for tech, occ in sorted(
        ((t, len(v)) for t, v in data["technique_index"].items()), key=lambda x: -x[1]
    ):
        print(f"  {tech:24} files={occ}")
    return 0
