---
module_id: proto-repository-analysis
kind: protocol
task_types: [repo-analysis, onboarding]
priority: 60
activation: resolver
---

# Protocol — Repository Analysis

1. Map structure: top-level dirs, entry points, build/test configs, CI.
2. Read README, CONTRIBUTING, package manifests (pyproject/package.json/lockfiles).
3. Identify: language versions, dependency graph, test runner, lint/typecheck commands.
4. Trace the main execution path (entry → core → I/O).
5. Note conventions (naming, error handling, config style) before editing.
6. Output a component map + "how to run tests" summary; flag unknowns as unknowns.
