# Release Report — v0.1.0

## Implementation summary

Built `hermes-instruction-pack` (HIP) end-to-end per master spec: environment audit → source acquisition (12/12 units, 80 files, SHA-256 provenance) → classification (14-category engine + curated labels) → normalization (4 personas with kept/removed provenance) → core instruction set (6 modules) → protocols (8) → resolver + validator → Hermes v0.21.0 adapter (check/install/dry-run/rollback/uninstall) → CLI (`hip`, 15 subcommands) → 32 automated tests (all passing) → analysis/security/conflict/duplicate reports → docs/changelog/licenses.

## Environment

Termux Android 16 aarch64; Python 3.14.6; pytest 9.1.1; Git 2.55; Hermes Agent v0.21.0 @ `~/.hermes` (commit 05f548f3, venv Py 3.13.13). Network egress OK (GitHub API + raw).

## Sources

- Fetched OK: 9 gists (jczzbczz-rgb), 1 pinned gist revision, togg53192-cmd/jailbreaks (31 files @ ec0517ff), Mrzimia99/hellowork (39 files @ bc094c07)
- Failed: 0
- Local `~/hellowork` identified as different fork (yeeiznix) — not used as source of record

## Modules shipped

- core: builder, persistence, recovery, tool-use, verification, instruction-priority
- personas: rat, eni, seraph, axiom (resolver-selected, single-active, bounds documented)
- protocols: project-planning, repository-analysis, autonomous-coding, debugging, research, testing, code-review, safe-automation

## CLI (verified)

inspect, sources list/import/audit, classify, normalize, modules list/validate, resolve, adapter check/install/rollback/uninstall, test, report — real behavior, proper exit codes, no fake success paths.

## Hermes integration status

- `adapter check`: compatible=True (v0.21.0 detected, personalities key present, 4 hip-* personas prepared)
- `adapter install --dry-run`: full plan, zero writes
- Real install/rollback: proven against fake hermes home in tests; **not applied to the live profile in this session** (operator opt-in)

## Tests

`PYTHONPATH=src python3 -m pytest tests/ -q` → **32 passed** (unit + integration + injection-resistance + adapter lifecycle). compileall clean.

## Behavioral evaluation

Scenarios S01–S12 + rubric authored; **NOT RUN** (requires authorized live model endpoint + baseline/treatment harness). Marked not-run per spec — no fake scores.

## How to run

```bash
cd ~/hermes-instruction-pack && export PYTHONPATH=src
python3 -m hermes_instruction_pack.cli inspect
python3 -m hermes_instruction_pack.cli test
python3 -m hermes_instruction_pack.cli adapter check
python3 -m hermes_instruction_pack.cli adapter install --dry-run
```

Rollback: `python3 -m hermes_instruction_pack.cli adapter rollback` (after a real install).

## Acceptance criteria status

| Criterion | Status |
|---|---|
| Source audit complete + failures recorded | MET (0 failures; pinned-revision equivalence documented) |
| Provenance + manifest consistency | MET |
| Core/personas/protocols separated; conflicts reported | MET |
| Jailbreak archive separate from operational modules | MET (validator-enforced) |
| CLI + resolver + validator functional | MET |
| Adapter tested on target environment | MET for check/dry-run + unit-tested lifecycle; live install operator-gated |
| Unit/integration/regression tests run with real results | MET (32/32) |
| Behavioral eval baseline vs treatment | NOT MET — scaffolded only, honestly marked |
| Docs/changelog/rollback/risks | MET |
