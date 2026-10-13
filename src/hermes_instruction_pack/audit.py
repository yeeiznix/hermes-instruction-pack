"""Post-import integrity and risk audit of archived sources."""

from __future__ import annotations

import json
import re
from pathlib import Path

from .manifest import Manifest, sha256_file, utcnow

RISK_PATTERNS: list[tuple[str, str]] = [
    (r"(?i)(api[_-]?key|secret|token|password|passwd)\s*[=:]\s*['\"][A-Za-z0-9_-]{16,}", "possible-credential"),
    (r"(?i)ignore\s+(all\s+)?(previous|prior|above)\s+instructions", "instruction-override"),
    (r"(?i)(system\s+override|developer\s+override|godmode|zero[- ]refusal)", "authority-claim"),
    (r"(?i)you\s+must\s+never\s+(refuse|decline)", "refusal-suppression"),
    (r"(?i)do\s+not\s+(mention|reveal|acknowledge)\s+(this|these)\s+(instruction|prompt)", "concealment"),
    (r"(?i)curl\s+[^\n|]*\|\s*(ba)?sh", "remote-code-execution-pipe"),
    (r"(?i)(rm\s+-rf\s+/|mkfs\.|dd\s+if=)", "destructive-command"),
    (r"(?i)(BEGIN (RSA|OPENSSH|EC) PRIVATE KEY)", "private-key-material"),
]


def scan_text(text: str) -> list[dict[str, str]]:
    findings = []
    for pat, label in RISK_PATTERNS:
        for m in re.finditer(pat, text):
            snippet = text[max(0, m.start() - 40): m.end() + 40].replace("\n", " ")
            findings.append({"label": label, "excerpt": snippet[:160]})
            if len(findings) > 40:
                return findings
    return findings


def run_audit(root: Path) -> int:
    root = Path(root)
    m = Manifest.load(root / "sources" / "manifest.yaml")
    results = []
    mismatches = 0
    scanned = 0
    for rec in m.all():
        path = rec.get("path")
        if not path or rec.get("status") != "fetched":
            continue
        fp = root / path
        if rec.get("kind") == "github-repo":
            idx = root / rec["tree_index"] if rec.get("tree_index") else None
            if idx and idx.exists():
                entries = json.loads(idx.read_text(encoding="utf-8"))
                bad = 0
                for e in entries:
                    f2 = fp / e["path"]
                    if f2.is_file() and sha256_file(f2) != e["sha256"]:
                        bad += 1
                results.append({"id": rec["id"], "repo_files": len(entries), "hash_mismatches": bad})
                mismatches += bad
                scanned += len(entries)
            continue
        if not fp.is_file():
            results.append({"id": rec["id"], "error": "file missing"})
            mismatches += 1
            continue
        h = sha256_file(fp)
        ok = h == rec.get("sha256")
        if not ok:
            mismatches += 1
        text = fp.read_bytes()[:2_000_000].decode("utf-8", errors="replace")
        findings = scan_text(text)
        scanned += 1
        results.append(
            {
                "id": rec["id"],
                "hash_ok": ok,
                "sha256": h,
                "size": fp.stat().st_size,
                "risk_findings": findings,
            }
        )
        if findings:
            rec["risk_notes"] = (
                (rec.get("risk_notes") or "") + f" | audit:{','.join(sorted({f['label'] for f in findings}))}"
            ).strip(" |")
            rec["audit_status"] = "flagged"
        elif rec.get("audit_status") == "pending":
            rec["audit_status"] = "reviewed"
    out = {
        "audited_at": utcnow(),
        "files_scanned": scanned,
        "hash_mismatches": mismatches,
        "results": results,
    }
    reports = root / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    outp = reports / "source-audit.json"
    outp.write_text(json.dumps(out, indent=1), encoding="utf-8")
    m.save()
    print(f"audit: scanned={scanned} mismatches={mismatches} -> {outp}")
    return 0 if mismatches == 0 else 1
