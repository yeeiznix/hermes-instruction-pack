---
module_id: proto-testing
kind: protocol
task_types: [testing, verification]
priority: 60
activation: resolver
requires_modules: [core-verification]
---

# Protocol — Testing

1. Identify the runner and existing patterns (pytest layout, fixtures, naming).
2. Cover: happy path, edge cases, error paths, and regressions being fixed.
3. Tests must assert real behavior — not tautologies or mocked-out cores.
4. Run the narrowest relevant suite during development; full suite before declaring done.
5. Report exact commands and outcomes; mark unrun suites as not run.
6. Never modify tests to hide failures without explicit justification to the operator.
