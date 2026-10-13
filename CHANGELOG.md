# Changelog

## 0.1.0 — 2026-10-12

### Added
- Phase A environment audit (`reports/environment-audit.md`)
- Source acquisition pipeline: gist user enumeration, pinned revision fetch, git repo clone; idempotent with versioned backups (`src/hermes_instruction_pack/importer.py`)
- 12/12 spec sources archived under `sources/` with SHA-256 manifest
- Integrity/risk audit (`hip sources audit`), 80 files scanned, 0 mismatches
- Classification engine + curated labels (`hip classify` → `analysis/classification.yaml`, `source-inventory.yaml`)
- Normalization with provenance (`hip normalize` → 4 persona modules)
- Core instruction set: builder, persistence, recovery, tool-use, verification, instruction-priority
- Task protocols: project-planning, repository-analysis, autonomous-coding, debugging, research, testing, code-review, safe-automation
- Module registry, resolver (task_type + single persona + dependency pull), validator (schema + banned-pattern + archive separation)
- CLI: inspect, sources list/import/audit, classify, normalize, modules list/validate, resolve, adapter check/install/rollback/uninstall, test, report
- Hermes adapter for v0.21.0: `agent.personalities` registration with backup/dry-run/rollback; optional `agent.instructions` append
- Test suite (32 tests: manifest, importer, classifier, normalizer, resolver, validator, CLI, prompt-injection, adapter)
- Evaluation scenarios (12) + scoring rubric + config (status: scaffolded-not-run)
- Conflict report, duplicate report, risk report, security report

### Known gaps
- Behavioral evaluation vs live model not executed
- jailbreaks-repo deep per-file technique index partially covered by corpus-level classification
- `hip` not pip-installed system-wide in this environment (PYTHONPATH invocation used)
