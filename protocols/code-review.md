---
module_id: proto-code-review
kind: protocol
task_types: [review]
priority: 55
activation: resolver
---

# Protocol — Code Review

1. Read the diff in context (not just changed lines).
2. Check: correctness, error handling, security (injection, secrets, path handling), performance hotspots, maintainability.
3. Look for side effects: config drift, backward-compat breaks, resource leaks.
4. Order findings by severity with file:line references.
5. Distinguish blocking issues from suggestions.
6. Never call a review complete without reading every changed file.
