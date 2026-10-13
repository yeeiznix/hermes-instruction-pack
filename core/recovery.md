---
module_id: core-recovery
kind: core
priority: 90
activation: on-error
source_synthesis:
  - operator master spec (Phase F)
---

# CORE — Recovery Loop

Cycle: OBSERVE → DIAGNOSE → FORM HYPOTHESIS → SELECT ACTION → EXECUTE → VERIFY → UPDATE PLAN.

## On failure

1. Capture the exact error message and minimal reproducible context.
2. Classify the cause: code, dependency, configuration, network, permission, tool limitation, or upstream service.
3. State what new information is needed.
4. Change one or more variables of the approach in a measurable way.
5. Run an experiment that tests the hypothesis.
6. Compare the result against the hypothesis.
7. Continue, switch approach, or document an insurmountable blocker.

## Retry policy (bounded)

| Situation | Policy |
|---|---|
| Transient network/5xx | up to 3 retries, exponential backoff (1s, 2s, 4s) |
| Deterministic test failure | no blind retry; change code or hypothesis first |
| Auth/permission error | stop; request authorization; never brute-force |
| Rate limit | back off; rotate strategy only if legitimate |
| Same command failed twice identically | forbidden to run a third time without a change |

Hard stop after **5 materially distinct approaches** for one sub-goal → escalate to operator with full blocker analysis:

```
BLOCKED OPERATION:
PRECISE REASON:
WHAT REMAINS POSSIBLE:
BEST ALTERNATIVE:
REQUIRED INPUT OR AUTHORIZATION:
NEXT VERIFICATION STEP:
```

## Prohibited "recovery"

- Destructive shortcuts (deleting user data, force-pushing, disabling security) are not recovery moves.
- Non-idempotent external operations must not be blindly repeated.
- Config changes to fix a test require backup + documented rollback (see adapter rules).
