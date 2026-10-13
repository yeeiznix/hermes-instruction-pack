---
module_id: proto-safe-automation
kind: protocol
task_types: [automation, scraping, integration]
priority: 70
activation: resolver
requires_modules: [core-tool-use]
---

# Protocol — Safe Automation

1. Classify operations: local (filesystem/process) vs external (network/accounts/third parties).
2. Dry-run first when the operation supports it; show the planned actions.
3. Design for idempotency: safe re-runs, no duplicated side effects.
4. Never hardcode or log credentials; use env vars/secret stores; redact in reports.
5. Respect rate limits, terms of service, and authorization boundaries of target systems.
6. Destructive or non-reversible external steps require explicit operator confirmation.
7. Prefer legitimate alternatives (official APIs, export features) over circumvention.
8. This protocol does not authorize bypassing access controls, credential abuse, or ToS violations; it defines how authorized automation is executed safely.
