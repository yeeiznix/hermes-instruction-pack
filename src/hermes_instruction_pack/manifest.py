"""Source manifest model: load, mutate, save sources/manifest.yaml."""

from __future__ import annotations

import datetime
import hashlib
from pathlib import Path
from typing import Any

import yaml

MANIFEST_VERSION = 1

REQUIRED_FIELDS = (
    "id",
    "kind",
    "url",
    "status",
    "audit_status",
)

VALID_KINDS = {"gist", "gist-pinned", "github-repo"}
VALID_STATUS = {"fetched", "failed", "skipped", "pending"}
VALID_AUDIT = {"pending", "reviewed", "flagged", "rejected"}


def utcnow() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Manifest:
    def __init__(self, data: dict[str, Any], path: Path):
        self.data = data
        self.path = path

    @classmethod
    def load(cls, path: Path) -> "Manifest":
        if path.exists():
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        else:
            data = {}
        data.setdefault("version", MANIFEST_VERSION)
        data.setdefault("generated_at", utcnow())
        data.setdefault("sources", [])
        return cls(data, path)

    def save(self) -> None:
        self.data["generated_at"] = utcnow()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            yaml.safe_dump(self.data, f, sort_keys=False, allow_unicode=True, width=100)

    def get(self, source_id: str) -> dict[str, Any] | None:
        for s in self.data["sources"]:
            if s.get("id") == source_id:
                return s
        return None

    def upsert(self, record: dict[str, Any]) -> dict[str, Any]:
        missing = [k for k in REQUIRED_FIELDS if k not in record]
        if missing:
            raise ValueError(f"manifest record missing required fields: {missing}")
        existing = self.get(record["id"])
        if existing is None:
            existing = dict(record)
            self.data["sources"].append(existing)
            return existing
        existing.update(record)
        return existing

    def all(self) -> list[dict[str, Any]]:
        return list(self.data["sources"])

    def by_status(self, status: str) -> list[dict[str, Any]]:
        return [s for s in self.data["sources"] if s.get("status") == status]

    def counts(self) -> dict[str, int]:
        out: dict[str, int] = {"total": len(self.data["sources"])}
        for s in self.data["sources"]:
            out[s.get("status", "?")] = out.get(s.get("status", "?"), 0) + 1
        return out
