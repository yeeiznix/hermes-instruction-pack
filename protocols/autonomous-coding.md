---
module_id: proto-autonomous-coding
kind: protocol
task_types: [feature, refactor, coding]
priority: 60
activation: resolver
requires_modules: [core-builder]
---

# Protocol — Autonomous Coding

1. Confirm the slice of work and its acceptance criteria.
2. Read neighboring code; match conventions exactly (imports, naming, error style).
3. Implement the smallest complete change that satisfies the criteria.
4. Wire real behavior end-to-end — no placeholder returns, no fake success paths.
5. Run targeted tests + the project's lint/typecheck after the change.
6. Fix failures before moving on; keep diffs focused (no drive-by refactors).
7. Summarize: files changed, commands run, results, remaining gaps.
