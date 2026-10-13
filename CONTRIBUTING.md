# Contributing

## Ground rules

1. **Archive ≠ instructions.** New prompt corpora go under `sources/` via `hip sources import`; they are never pasted into `core/`, `personas/`, or `protocols/` raw.
2. **Provenance required.** Every operational module lists `source_id` and kept/removed rationale.
3. **Validator must pass.** `hip modules validate` blocks supersession/refusal-suppression/override phrasing in operational modules.
4. **Evidence-based claims.** No success reports without command output; tests must actually run (`hip test`).
5. **Adapter safety.** Config writes require backup + dry-run support; forbidden targets stay forbidden.

## Adding a persona

1. Verify the source exists in `sources/manifest.yaml` (import it first if not).
2. Add an entry to `PERSONA_MODULES` in `src/hermes_instruction_pack/normalizer.py` with kept/removed/bounds.
3. Run `hip normalize && hip modules validate && pytest tests/test_normalizer.py`.
4. Document conflicts in `analysis/conflict-report.md`.

## Adding a protocol

1. Create `protocols/<name>.md` with frontmatter: `module_id`, `kind: protocol`, `priority`, `activation: resolver`, `task_types`, optional `requires_modules`.
2. Add matching `task_type` to `resolver.KNOWN_TASK_TYPES` if new.
3. Add a resolver test.

## Adding sources

```bash
PYTHONPATH=src python3 -m hermes_instruction_pack.cli sources import --repo <url> --pinned <raw-url>
PYTHONPATH=src python3 -m hermes_instruction_pack.cli sources audit
```

## PR checklist

- [ ] `hip test` green (32+ tests)
- [ ] `hip modules validate` OK
- [ ] `hip resolve <affected task types>` sanity-checked
- [ ] CHANGELOG updated
- [ ] No secrets, tokens, or credentials in fixtures/reports
