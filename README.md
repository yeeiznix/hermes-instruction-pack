# Hermes Instruction Engineering Pack (hip)

Modular instruction system for AI coding agents: audited sources → classified prompts → normalized personas/protocols → resolver + validator → Hermes Agent adapter → tests.

**Design stance:** imported jailbreak/persona texts are *data to analyze*, never instructions to activate. Operational modules are normalized derivatives with provenance; the validator bans supersession/refusal-suppression patterns outside the archive.

## Quick start

```bash
cd ~/hermes-instruction-pack
export PYTHONPATH=src
python3 -m hermes_instruction_pack.cli inspect
python3 -m hermes_instruction_pack.cli sources import --spec   # idempotent fetch
python3 -m hermes_instruction_pack.cli sources audit
python3 -m hermes_instruction_pack.cli classify
python3 -m hermes_instruction_pack.cli normalize
python3 -m hermes_instruction_pack.cli modules validate
python3 -m hermes_instruction_pack.cli resolve coding --persona rat
python3 -m hermes_instruction_pack.cli test
python3 -m hermes_instruction_pack.cli adapter check
python3 -m hermes_instruction_pack.cli adapter install --dry-run
```

Install as a CLI (optional): `pip install -e .` → `hip …`

## What's in the box

| Area | Location |
|---|---|
| Source archive + manifest (SHA-256 provenance) | `sources/` |
| Classification / inventory / dedup / conflict / risk | `analysis/` |
| Core instructions (builder, persistence, recovery, tools, verification, priority) | `core/` |
| Personas (rat, eni, seraph, axiom) — optional, one at a time | `personas/` |
| Task protocols (planning, repo-analysis, coding, debugging, research, testing, review, safe automation) | `protocols/` |
| Jailbreak corpus (archive-only) | `archive/jailbreak-prompts/` + `sources/` |
| Hermes adapter (check/install/rollback) | `adapters/hermes/` + `src/.../adapter_hermes.py` |
| CLI (`hip`) | `src/hermes_instruction_pack/cli.py` |
| Tests (32) | `tests/` |
| Evaluation scenarios + rubric (scaffolded) | `evaluation/` |
| Reports | `reports/`, `analysis/` |

## Verified environment

- Termux/Android aarch64, Python 3.14.6 (system), pytest 9.1.1
- Hermes Agent v0.21.0 at `~/.hermes` (commit 05f548f3) — adapter `check` passes
- Full evidence: `reports/environment-audit.md`

## Safety properties

- Adapter never touches `agent.system_prompt`, `prefill_messages_file`, `.env`, `auth.json`
- Backup before every config write; `hip adapter rollback` restores
- Archive content is never resolved into sessions
- No fabricated test/eval scores; missing model ⇒ evaluation marked NOT RUN

## Documentation

- Architecture & usage: this file
- Conflict analysis: `analysis/conflict-report.md`
- Security: `reports/security-report.md`
- Adapter: `adapters/hermes/README.md`
- Changelog: `CHANGELOG.md`
- Rollback: `adapters/hermes/README.md#rollback` + git history of the pack

## Status

v0.1.0 — source audit complete (12/12), classification complete, 4 personas + 6 core + 8 protocols operational, CLI functional, 32/32 unit tests pass, Hermes adapter check+dry-run verified on target install. Behavioral model evaluation: scaffolded, not run.
