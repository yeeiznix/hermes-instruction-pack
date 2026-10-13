# Environment Audit — Hermes Instruction Engineering Pack

Date: 2026-10-12 (agent session)
Auditor: opencode agent (mimo-v2.6-flash-free) executing Phase A of the master spec.

## 1. Host platform

| Item | Value | Evidence |
|---|---|---|
| OS / kernel | Android 16 GKI, Linux 6.12.38-android16-5 (aarch64) | `uname -a` |
| Distribution | Termux (`/data/data/com.termux/files/usr`) | `command -v` paths |
| Filesystem | `/data/user/0` 227G total, 35G free (85% used) | `df -h` |
| Memory | 7.5 Gi total, ~2.2 Gi available at audit time | `free -h` |
| Working dir | `/data/data/com.termux/files/home` — **not a git repository** | `git status` → fatal |

The working directory contains ~200 pre-existing user files/projects (`fox/`, `muse/`, `hellowork/`, `jailbreaks/`, `hermes-jailbench/`, `.hermes/`, etc.). None of these were deleted or modified by this project. The new project lives in a fresh directory: `~/hermes-instruction-pack/`.

## 2. Language runtimes and tools

| Tool | Version / status | Notes |
|---|---|---|
| Python (system) | 3.14.6 at `$PREFIX/bin/python3` | primary runtime for this pack |
| pip | present | |
| pytest | 9.1.1 (`python3 -m pytest`) | test runner |
| PyYAML | 6.0.3 | manifest/config parsing |
| requests | present | HTTP client (importer) |
| Git | 2.55.0 | repo cloning |
| curl / wget | present | raw fetches; `/tmp` is not writable (curl exit 23), use `$PREFIX/tmp` |
| Node / npm | present | not required by this pack |
| ripgrep | present | analysis |
| gh | present | GitHub API fallback |
| uv / poetry / jq / fd | MISSING | pack must not depend on them |

Python 3.14 compatibility is a design constraint (no distutils, etc.). The pack targets `>=3.11`.

## 3. Network access

- Outbound HTTPS works through both `curl` and the agent webfetch tool (verified: `gist.github.com`, `api.github.com`, `gist.githubusercontent.com`).
- GitHub API rate limit at audit: 60 req/h unauthenticated, 55 remaining.
- Caveat: `curl -o /tmp/...` fails with exit 23 (write error). All temp files must go under `/data/data/com.termux/files/usr/tmp/opencode/`.

## 4. Hermes Agent installation (verified)

| Item | Value | Evidence |
|---|---|---|
| Source tree | `~/.hermes/hermes-agent/` — clone of `https://github.com/NousResearch/hermes-agent.git` | `git remote -v` |
| Version | 0.21.0 (`pyproject.toml`, `hermes_agent.egg-info/PKG-INFO`) | file read |
| HEAD | `05f548f3` ("fix(desktop): declare rememberLog state…"), no tags | `git log`, `git describe` |
| Venv Python | 3.13.13 (Clang 21) | `venv/bin/python -V` |
| Entry point | `~/.hermes/hermes` bash wrapper → `venv/bin/python .hermes/hermes-agent/hermes` | wrapper file read |
| CLI health | `hermes --help` runs and prints full command list | executed |
| Runtime data | `~/.hermes/` (config.yaml v40, state.db, skills/, sessions/, …) | directory listing |

### 4.1 Instruction / persona integration mechanisms (verified against source)

Read from `hermes_cli/personality.py`, `hermes_cli/config_defaults.py`, and the live `~/.hermes/config.yaml`:

1. **`agent.instructions`** — YAML list of file paths appended to the prompt context. Currently: `~/.hermes/skills/fox-jb-auto/SKILL.md` and its `MANIFEST.json`.
2. **`agent.personalities`** — dict `name -> prompt text` (str or list). User entries overlay `BUILTIN_PERSONALITIES` (helpful/concise/kawaii/pirate/…). Currently **empty**.
3. **`display.personality`** — holds the *name* of the active personality overlay (never prompt text).
4. **`agent.system_prompt`** — user-owned manual overlay; personality code never writes it. Currently contains a user-supplied "SYADAGENTIC" protocol (pre-existing; **not modified by this project**).
5. **Skills** — `~/.hermes/skills/<name>/SKILL.md` with YAML frontmatter (`name`, `description`, `version`, `author`, `license`, `platforms`, `metadata.hermes.tags`, `prerequisites`). Managed by `hermes skills install|list|inspect|audit|uninstall` (agentskills.io-compatible standard).
6. **`hermes config get|set|unset|check`** — official config mutation path; supports backups elsewhere in CLI (`hermes backup` exists too).

### 4.2 Constraints for the adapter

- The user's `~/.hermes/config.yaml` contains live credentials/paths and a 245 KB system_prompt. The adapter MUST: (a) never print `.env`/`auth.json` contents, (b) make a timestamped backup before any `config set`, (c) register personas under `hip.*` names to avoid clobbering built-ins, (d) support rollback.
- The `hermes` wrapper shebang (`#!/usr/bin/env bash`) fails when invoked as `/usr/bin/env`-relative on Android; it must be run as `bash ~/.hermes/hermes …` or through the venv python. The adapter should invoke it via the venv python path discovered at install time.
- No Hermes-internal hooks may be patched; only official surfaces (`config`, `skills`, `instructions`, `personalities`) are used.

## 5. Local copies of the target sources

| Local dir | Git remote | Relationship to spec source |
|---|---|---|
| `~/jailbreaks/` | `https://github.com/togg53192-cmd/jailbreaks` | exact match; HEAD `91ca215` (repo pushed 2026-10-10, clone may be slightly stale) |
| `~/hellowork/` | `https://github.com/yeeiznix/hellowork.git` | **different repo** (fork lineage "Fox JB Framework"); NOT `Mrzimia99/hellowork` |
| `~/hermes-jailbench/` | (not checked into this audit's scope) | adjacent jailbreak-benchmark project, out of scope |

`Mrzimia99/hellowork` exists remotely (API: default branch `main`, pushed 2026-10-12) and must be cloned fresh for this pack.

## 6. Pre-existing agent-configuration hazards (informational)

The following were observed while verifying integration surfaces and are recorded for the security report, not acted upon:

- `~/.hermes/config.yaml.agent.system_prompt` currently loads a third-party "jailbreak protocol" document (SYADAGENTIC) — pre-existing user choice.
- `~/.hermes/config.yaml.prefill_messages_file` points at `~/hellowork/prefill_jb.json`.
- `~/.hermes/skills/fox-jb-auto/` is loaded via `agent.instructions`.

This project does not alter any of these. The pack's own modules are additive and independently enableable.

## 7. Test / lint tooling for this project

- Tests: `pytest` (9.1.1) — `python3 -m pytest tests/` from the project root.
- Lint: no ruff/flake8 installed system-wide; pack uses `python3 -m compileall` and pytest as the enforced gates. Optional ruff config is provided but not enforced in this environment.
- Packaging: plain `pyproject.toml` with setuptools backend; installable via `pip install -e .` (no uv/poetry dependency).

## 8. Audit conclusion

Phase A is complete. All items required by the master spec (OS, runtimes, Git, package managers, Hermes installation, config/skill/persona mechanisms, network, initial Git state, test method) have been inspected with direct evidence. No Hermes config or unrelated user file was modified.

**Open items carried forward:**
- `/tmp` unwritable → importer must use `$PREFIX/tmp/opencode`.
- `~/jailbreaks/` clone may be behind upstream → pack does its own fresh clone under `sources/github/`.
- Behavioral evaluation against a live model is **not** run in Phase A; it requires a reachable model endpoint and is tracked separately in Phase M.
