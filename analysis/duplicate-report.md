# Duplicate Report — Phase D

Method: SHA-256 equality (exact) + size/name heuristics (near). Evidence: `sources/manifest.yaml`, `sources/raw-api/tree-*.json`.

## Exact duplicates

| Content | Copies | SHA-256 (12) |
|---|---|---|
| gist 5590e4ad (HTML game) current head | `sources/gists/gist-5590e4ad/`, `sources/gists/gist-pinned-aaa10d10/`, `repo-Mrzimia99-hellowork/5590e4ad_gistfile1.txt`, `repo-Mrzimia99-hellowork/gists/5590e4ad_gistfile1.txt` | 7950dbb9064a |
| gist a7dc501b | `sources/gists/gist-a7dc501b/` + 2 hellowork copies | d5be1bb58b56 |
| gist 9783f763 | `sources/gists/gist-9783f763/` + 2 hellowork copies | acb0b2e248e4 |
| gist 1525b7f5 | `sources/gists/gist-1525b7f5/` + 2 hellowork copies | 3dd5d799c2a3 |
| gist 3ecdb273 | `sources/gists/gist-3ecdb273/` + 2 hellowork copies | 71c0592876e8 |
| gist f3a4f106 | `sources/gists/gist-f3a4f106/` + 2 hellowork copies | e7e1244c6f33 |
| gist c8503378 | `sources/gists/gist-c8503378/` + 2 hellowork copies | cb24600b448d |
| gist 82dd0ed5 | `sources/gists/gist-82dd0ed5/` + 2 hellowork copies | 004cb1612af5 |

## Near-duplicates / divergent revisions

| Item | Detail | Handling |
|---|---|---|
| gist 8189a15e | root + `sources/gists` copies = 20000 B (c3696cc671cf); `hellowork/gists/` copy = 15000 B → older revision (gist updated 2026-09-21) | Keep both archived; manifest records sizes/hashes; analysis uses newest (20000 B) |
| deepseek family | `deepseek v3.md` (12683) ≈ `deepseek v4.md` (13120) ≈ `deepseek-4-1.md` (14788) in jailbreaks repo — version lineage, not identical | All archived separately; classification groups under jailbreak corpus |
| glm family | `glm-5.2.md`, `glm-5-3-flash.md`, `glm-zcode-*`, `glm5-3opencode.md` share structure | same |
| sonnet/opus family | `sonnet v1/v2`, `opus v1/v2` | same |
| local `~/hellowork` (yeeiznix fork) vs `Mrzimia99/hellowork` | Same lineage, different file sets (local lacks modules/, google-bulk-login.py; both lack fresh sync) | Pack uses fresh Mrzimia99 clone only; local fork untouched |

## Dedup policy applied

- Canonical copy for each gist = `sources/gists/gist-<id>/` (direct raw fetch, hash-verified).
- Repo copies retained for provenance of those repos (never deleted).
- Normalization (personas) references canonical gist IDs only.
- No file was removed; dedup is advisory + canonical-pointer based.
