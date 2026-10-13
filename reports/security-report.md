# Security Report — Hermes Instruction Engineering Pack

Date: 2026-10-12. Scope: pack pipeline + archived corpus + adapter behavior on the target Termux/Hermes host.

## Controls verified

| Control | Evidence |
|---|---|
| No execution of imported code | importer only fetches/clones; tests use fakes; `rg` confirms no `subprocess` on corpus files |
| Path confinement | importer writes under `sources/`; adapter writes only `~/.hermes/config.yaml` + pack-local backups |
| Secret hygiene | no credentials in manifest/fixtures/reports; adapter never prints `.env`/`auth.json`; pattern scan found 0 private keys/credential assignments |
| Config change safety | backup-before-write, dry-run mode, rollback command, install-state audit file (`tests/test_adapter.py`) |
| Instruction integrity | archive never selected by resolver (`tests/test_prompt_injection.py`); validator bans override patterns in operational modules |
| Prompt-injection handling | repo/README text treated as data (S07 scenario; core/instruction-priority.md) |
| Dependency surface | only PyYAML + requests (runtime); pytest (dev). No npm/cargo deps for the pack |

## Findings

See `analysis/risk-report.md` for corpus risks (autoinjector, bulk-login tooling, jailbreak corpus). Summary:

- HIGH (archived, unexecuted): fox-autoinject config mutator; google-bulk-login credential automation
- MEDIUM (data-only): 31-file per-model jailbreak corpus; 9 persona/jailbreak gists
- Info: pre-existing user config already wires fox-jb-auto instructions + prefill; pack does not modify

## Residual risk

- Operator-side: `hip adapter install` modifies a live Hermes config (with backup). A bad manual edit between backup and rollback could confuse restores; mitigations: backups accumulate, git-track pack state.
- Corpus redistribution: unclear licenses (see LICENSES.md).
- `git clone` of hostile repos could run remote hooks in theory; clones performed with default settings — recommend `GIT_CONFIG_GLOBAL=/dev/null` hygiene for hostile corpora in future revisions.

## Recommendations

1. Run `hip adapter check` after any Hermes upgrade.
2. Keep `allow_raw_source_activation: false` (config/defaults.yaml).
3. Before enabling evaluation against live models, review scenario S11/S12 outputs for unsafe-action compliance.
4. Rotate GitHub token scope if one is later used for imports (currently unauthenticated).
