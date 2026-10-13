# Risk Report — Source Corpus & Pipeline

Scope: archived sources (12 units / 80 files) + import/normalize pipeline. Complements reports/source-audit.json (hash/risk-pattern scan).

## Findings

### R1 — Auto-injector mutates agent runtime instructions (HIGH, archived)

- Where: `repo-Mrzimia99-hellowork/fox-autoinject.py`, `fox-jb-install.sh`, README_FOX_JB.md
- What: designed to download gist protocols and inject them as Hermes runtime instructions/prefills (`prefill_messages_file`, instruction paths).
- Evidence: README_FOX_JB.md "Auto-Activation" section; prefill_jb.json (17 KB of system-message payloads).
- Status: archived, never executed by this pack. Pack adapter uses explicit install + backup instead.
- Recommendation: do not run autoinject against a live profile; if encountered, treat config diff as incident.

### R2 — Bulk credential automation tool (HIGH, archived)

- Where: `repo-Mrzimia99-hellowork/google-bulk-login.py`
- What: bulk login automation (credential use at scale).
- Status: archived unexecuted; classification decision `archive` with category `credential-automation-risk`.
- Recommendation: out of scope for this pack; requires explicit authorization regimes that this pack does not provide.

### R3 — Jailbreak prompt corpus (MEDIUM as data, HIGH if activated)

- Where: `sources/github/repo-togg53192-cmd-jailbreaks/` (31 files), all jczzbczz-rgb gists.
- What: per-model bypass prompts, supersession/authority claims, encoded payloads.
- Status: archive-only. Operational modules are normalized derivatives without bypass logic.
- Recommendation: use strictly as injection-resistance fixtures (evaluation/), never as session instructions.

### R4 — Destructive-command pattern in fiction gist (LOW)

- Where: `gist-82dd0ed5` (CHRONICLE_ENGINE), 1 regex hit (`destructive-command`).
- Context: in-story technical fiction, not an operational directive for this pack.
- Status: documented; no action beyond archive flag.

### R5 — Pre-existing live config hazards on this machine (INFORMATIONAL)

- `~/.hermes/config.yaml` already loads `fox-jb-auto` via `agent.instructions` and points `prefill_messages_file` at `~/hellowork/prefill_jb.json`; `agent.system_prompt` contains a supersession protocol.
- Not modified by this project (verified: adapter runs in dry-run unless install confirmed).
- Recommendation: operator may audit these separately; `hip adapter install` reports them as environment warnings.

### R6 — Pipeline handling of untrusted text (MITIGATED)

- Imported text is treated as data (classifier/normalizer never execute it).
- No credential material found by pattern scan (0 private-key/credential-assignment hits).
- Importer stores raw bytes + SHA-256; changes are versioned (`.v<timestamp>` backups), never silently overwritten.
- Validator bans supersession/refusal-suppression/override phrases in operational modules (exception flag only for instruction-priority meta-doc, warned).

## Residual risks (accepted, documented)

- Normalized personas are style distillations; if a consumer concatenates raw source files instead of modules, R3 resurfaces.
- Unauthenticated GitHub API rate limit (60/h) can throttle re-imports.
- No sandboxing of `git clone` beyond no-execution policy (git hooks from untrusted remotes: clones used `--quiet` standard clone; recommend `git config --global core.hooksPath /dev/null` hygiene for hostile corpora — operator decision).
