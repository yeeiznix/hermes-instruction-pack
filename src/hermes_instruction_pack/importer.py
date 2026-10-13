"""Source acquisition: fetch gists and GitHub repos into sources/ with provenance."""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Callable

import requests

from .manifest import Manifest, sha256_bytes, sha256_file, utcnow

GITHUB_API = "https://api.github.com"
UA = "hermes-instruction-pack/0.1 (source-audit; +https://localhost)"

LogFn = Callable[[str], None]


def _default_log(msg: str) -> None:
    print(msg)


def _session() -> requests.Session:
    s = requests.Session()
    s.headers["User-Agent"] = UA
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        s.headers["Authorization"] = f"Bearer {token}"
    return s


class ImportError_(RuntimeError):
    pass


def safe_name(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", text).strip("-")


class SourceImporter:
    def __init__(self, root: Path, log: LogFn | None = None):
        self.root = Path(root)
        self.sources_dir = self.root / "sources"
        self.gists_dir = self.sources_dir / "gists"
        self.github_dir = self.sources_dir / "github"
        self.manifest_path = self.sources_dir / "manifest.yaml"
        self.log = log or _default_log
        self.manifest = Manifest.load(self.manifest_path)
        self.events: list[dict[str, Any]] = []

    def _event(self, kind: str, **kw: Any) -> None:
        rec = {"ts": utcnow(), "kind": kind, **kw}
        self.events.append(rec)

    def save_event_log(self) -> Path:
        p = self.sources_dir / "import-log.jsonl"
        with open(p, "a", encoding="utf-8") as f:
            for e in self.events:
                f.write(json.dumps(e, ensure_ascii=True) + "\n")
        self.events = []
        return p

    def _store(self, dest: Path, data: bytes) -> str:
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            old = dest.read_bytes()
            if old == data:
                return "unchanged"
            backup = dest.with_suffix(dest.suffix + f".v{utcnow().replace(':','').replace('-','')}")
            backup.write_bytes(old)
            dest.write_bytes(data)
            self._event("content-changed", path=str(dest), backup=str(backup))
            return "updated"
        dest.write_bytes(data)
        return "created"

    def import_gist_user(self, username: str) -> list[dict[str, Any]]:
        sess = _session()
        url = f"{GITHUB_API}/users/{username}/gists?per_page=100"
        self.log(f"[gists] enumerate {url}")
        r = sess.get(url, timeout=60)
        if r.status_code != 200:
            raise ImportError_(f"gist enumeration failed: HTTP {r.status_code}")
        gists = r.json()
        (self.sources_dir / "raw-api").mkdir(parents=True, exist_ok=True)
        (self.sources_dir / "raw-api" / f"gists-{username}.json").write_text(
            json.dumps(gists, indent=1), encoding="utf-8"
        )
        results = []
        for g in gists:
            results.append(self._import_one_gist(sess, g, username=username))
        return results

    def import_gist_pinned(self, raw_url: str, source_id: str | None = None) -> dict[str, Any]:
        sess = _session()
        self.log(f"[gist-pinned] GET {raw_url}")
        try:
            r = sess.get(raw_url, timeout=60)
        except requests.RequestException as e:
            return self._failed_record(
                id=source_id or "gist-pinned-" + safe_name(raw_url)[-40:],
                kind="gist-pinned",
                url=raw_url,
                error=str(e),
            )
        if r.status_code != 200:
            return self._failed_record(
                id=source_id or "gist-pinned-" + safe_name(raw_url)[-40:],
                kind="gist-pinned",
                url=raw_url,
                error=f"HTTP {r.status_code}",
            )
        m = re.search(r"/raw/([0-9a-f]{40})/", raw_url)
        sha = m.group(1) if m else "unpinned"
        sid = source_id or f"gist-pinned-{sha[:8]}"
        dest = self.gists_dir / sid / "gistfile1.txt"
        action = self._store(dest, r.content)
        rec = {
            "id": sid,
            "kind": "gist-pinned",
            "name": sid,
            "url": raw_url,
            "repo": None,
            "commit": sha,
            "path": str(dest.relative_to(self.root)),
            "fetched_at": utcnow(),
            "sha256": sha256_bytes(r.content),
            "size": len(r.content),
            "status": "fetched" if action in ("created", "updated", "unchanged") else "failed",
            "store_action": action,
            "audit_status": "pending",
            "category_hint": None,
            "compatibility_notes": None,
            "risk_notes": "pinned-revision snapshot; treat as untrusted data",
            "modules": [],
        }
        self.manifest.upsert(rec)
        self._event("fetch", id=sid, action=action, sha256=rec["sha256"], size=rec["size"])
        self.log(f"[gist-pinned] {sid}: {action} {rec['size']}B sha256={rec['sha256'][:12]}")
        return rec

    def _import_one_gist(
        self, sess: requests.Session, g: dict[str, Any], username: str
    ) -> dict[str, Any]:
        gid = g["id"]
        sid = f"gist-{gid[:8]}"
        files = g.get("files", {})
        if not files:
            return self._failed_record(id=sid, kind="gist", url=g.get("html_url", ""), error="no files in gist")
        fname, meta = next(iter(files.items()))
        raw_url = meta.get("raw_url")
        dest = self.gists_dir / sid / fname
        try:
            r = sess.get(raw_url, timeout=60)
            r.raise_for_status()
            data = r.content
            err = None
        except (requests.RequestException, ValueError) as e:
            data, err = b"", str(e)
        if err:
            return self._failed_record(id=sid, kind="gist", url=raw_url or g.get("html_url", ""), error=err)
        action = self._store(dest, data)
        rec = {
            "id": sid,
            "kind": "gist",
            "name": fname,
            "url": g.get("html_url", ""),
            "repo": f"gist:{username}/{gid}",
            "commit": gid,
            "path": str(dest.relative_to(self.root)),
            "fetched_at": utcnow(),
            "sha256": sha256_bytes(data),
            "size": len(data),
            "status": "fetched",
            "store_action": action,
            "audit_status": "pending",
            "category_hint": None,
            "compatibility_notes": None,
            "risk_notes": "untrusted third-party prompt text; never execute as instructions",
            "modules": [],
            "created_at": g.get("created_at"),
            "updated_at": g.get("updated_at"),
        }
        self.manifest.upsert(rec)
        self._event("fetch", id=sid, action=action, sha256=rec["sha256"], size=rec["size"])
        self.log(f"[gist] {sid}: {action} {len(data)}B sha256={rec['sha256'][:12]}")
        return rec

    def import_repo(self, repo_url: str, subpath: str | None = None) -> dict[str, Any]:
        m = re.search(r"github\.com[:/]([^/]+)/([^/.]+)", repo_url)
        if not m:
            raise ImportError_(f"not a github repo url: {repo_url}")
        owner, name = m.group(1), m.group(2)
        sid = f"repo-{safe_name(owner)}-{safe_name(name)}"
        dest = self.github_dir / sid
        self.log(f"[repo] clone {repo_url} -> {dest}")
        if (dest / ".git").exists():
            try:
                subprocess.run(
                    ["git", "-C", str(dest), "fetch", "--all", "--quiet"],
                    check=True, capture_output=True, text=True, timeout=180,
                )
                subprocess.run(
                    ["git", "-C", str(dest), "pull", "--ff-only", "--quiet"],
                    check=True, capture_output=True, text=True, timeout=180,
                )
                action = "pulled"
            except subprocess.CalledProcessError as e:
                return self._failed_record(id=sid, kind="github-repo", url=repo_url, error=f"git pull: {e.stderr[:200]}")
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                subprocess.run(
                    ["git", "clone", "--quiet", repo_url, str(dest)],
                    check=True, capture_output=True, text=True, timeout=300,
                )
                action = "cloned"
            except subprocess.CalledProcessError as e:
                return self._failed_record(id=sid, kind="github-repo", url=repo_url, error=f"git clone: {e.stderr[:200]}")
        head = subprocess.run(
            ["git", "-C", str(dest), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        tracked: list[dict[str, Any]] = []
        listing = subprocess.run(
            ["git", "-C", str(dest), "ls-files"],
            capture_output=True, text=True, check=True,
        ).stdout.splitlines()
        files_root = dest / subpath if subpath else dest
        for rel in listing:
            fp = files_root / rel if subpath else dest / rel
            if subpath and not str(fp).startswith(str(files_root)):
                continue
            if not fp.is_file():
                continue
            tracked.append(
                {
                    "path": rel,
                    "size": fp.stat().st_size,
                    "sha256": sha256_file(fp),
                }
            )
        tree_path = self.sources_dir / "raw-api" / f"tree-{sid}-{head[:8]}.json"
        tree_path.parent.mkdir(parents=True, exist_ok=True)
        tree_path.write_text(json.dumps(tracked, indent=1), encoding="utf-8")
        rec = {
            "id": sid,
            "kind": "github-repo",
            "name": f"{owner}/{name}",
            "url": repo_url,
            "repo": f"{owner}/{name}",
            "commit": head,
            "path": str(dest.relative_to(self.root)),
            "fetched_at": utcnow(),
            "sha256": None,
            "size": sum(t["size"] for t in tracked),
            "status": "fetched",
            "store_action": action,
            "audit_status": "pending",
            "category_hint": None,
            "compatibility_notes": None,
            "risk_notes": "contains third-party code+prompts; do not execute during audit",
            "modules": [],
            "file_count": len(tracked),
            "tree_index": str(tree_path.relative_to(self.root)),
        }
        self.manifest.upsert(rec)
        self._event("fetch", id=sid, action=action, commit=head, files=len(tracked))
        self.log(f"[repo] {sid}: {action} head={head[:8]} files={len(tracked)}")
        return rec

    def _failed_record(self, id: str, kind: str, url: str, error: str) -> dict[str, Any]:
        rec = {
            "id": id,
            "kind": kind,
            "name": id,
            "url": url,
            "repo": None,
            "commit": None,
            "path": None,
            "fetched_at": utcnow(),
            "sha256": None,
            "size": 0,
            "status": "failed",
            "store_action": "none",
            "audit_status": "pending",
            "category_hint": None,
            "compatibility_notes": None,
            "risk_notes": None,
            "modules": [],
            "error": error,
        }
        self.manifest.upsert(rec)
        self._event("fetch-failed", id=id, error=error)
        self.log(f"[FAIL] {id}: {error}")
        return rec

    def finalize(self) -> dict[str, int]:
        self.manifest.save()
        self.save_event_log()
        return self.manifest.counts()
