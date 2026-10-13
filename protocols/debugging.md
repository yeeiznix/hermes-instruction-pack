---
module_id: proto-debugging
kind: protocol
task_types: [bugfix, debugging]
priority: 60
activation: resolver
requires_modules: [core-recovery]
---

# Protocol — Debugging

1. Reproduce the bug deterministically; capture the exact error and environment.
2. Read logs/stack traces fully; note the first meaningful frame.
3. Form 1-3 ranked hypotheses; design the cheapest discriminating test.
4. Change one variable per experiment; observe.
5. Fix the root cause, not the symptom; add a regression test.
6. Verify the fix and check adjacent paths for regressions.
7. If unreproducible: say so; propose instrumentation rather than guessing.
