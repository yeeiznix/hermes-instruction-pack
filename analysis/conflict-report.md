# Conflict Report — Instruction Corpus

Generated 2026-10-12 from classification of 12 source units (Phase C/D).

## Confirmed instruction conflicts (source → operational risk)

| # | Conflict | Sources | Resolution in this pack |
|---|---|---|---|
| 1 | **Supersession claims** ("MUST supersede", "highest priority layer", SUPERSESSION blocks) vs real instruction hierarchy | gist-a7dc501b, gist-9783f763, gist-8189a15e, majority of jailbreaks/* files, fox-autoinject design | All supersession text stays in `archive/`. Operational modules carry `core/instruction-priority.md` (priority 99) that explicitly rejects override claims. Validator bans supersession phrases in operational modules. |
| 2 | **Refusal suppression** ("never sorry/cannot/refuse", "zero refusal", "refusal = craft failure") vs honest limitation reporting | gist-a7dc501b, gist-8189a15e, jailbreaks corpus, involuntary.py module | Banned-pattern check in validator; recovery protocol requires precise blocker reporting instead. |
| 3 | **Fake authority frames** (Stillwater auditor ISO-42001 pretext; "Role: System Administrator" channel impersonation) vs real authorization | gist-f3a4f106, modules/role.py | Archived as technique analysis; not operationalized. Tool-use core requires demonstrated permissions. |
| 4 | **Mandatory persona activation** ("ALWAYS ACTIVE", identity-is-total claims) vs optional, explainable persona selection | gist-3ecdb273 ("ALWAYS ACTIVE"), gist-a7dc501b (identity-locked) | Personas are `activation: resolver`, default off, selectable/deselectable via `hip resolve --persona`. |
| 5 | **Obfuscated delivery** (base64 "kotak" payload) vs transparent instruction handling | gist-8189a15e | Archived with decode-for-analysis note; never auto-activated; import pipeline stores raw + hash. |
| 6 | **Absolute-competence claims** ("compilation must succeed on first attempt") vs evidence-gated verification | gist-8189a15e, jailbreaks/* | core/verification.md requires actual test runs; claims must cite evidence. |
| 7 | **Silent config injection** (fox-autoinject writes prefills/instructions into `~/.hermes` without per-change confirmation) vs least-privilege config changes | repo-Mrzimia99-hellowork (fox-autoinject.py, README_FOX_JB.md) | Pack adapter: backup + explicit `hip adapter install` + audit trail; never silent. |
| 8 | **Bulk credential automation** (google-bulk-login.py) vs credential-handling policy | repo-Mrzimia99-hellowork | Flagged `credential-automation-risk`; archived unexecuted; proto-safe-automation requires authorization + no credential logging. |
| 9 | **Style conflicts between personas** (rat: no performed structure vs seraph: fixed 3-block frame; eni: enthusiasm vs axiom: quiet) | gist-9783f763, gist-3ecdb273, gist-1525b7f5, gist-c8503378 | Mutual exclusion enforced: resolver errors on multiple personas; one persona per task. |
| 10 | **Content-license framing** (fiction engine treats story context as license for normally-restricted content) | gist-82dd0ed5 | Archived; never selected for operational tasks; injection tests use it as negative fixture. |

## Cross-persona incompatibility matrix

|  | rat | eni | seraph | axiom |
|---|---|---|---|---|
| rat | — | compatible* | style clash (structure) | compatible |
| eni | compatible* | — | compatible | tone clash (warmth vs quiet) |
| seraph | style clash | compatible | — | format clash |
| axiom | compatible | tone clash | format clash | — |

\*compatible when scoping differs (eni talks, rat builds); still single-persona-at-a-time policy.

## Unresolved / accepted risks

- Persona normalization removed bypass clauses, but base source texts remain in `sources/` by design (provenance). Anyone wiring raw sources into an agent would re-introduce conflicts 1-3; the adapter only installs normalized modules.
- `agent.system_prompt` on this machine already contains a user-supplied supersession protocol (pre-existing, untouched). Pack modules cannot neutralize it; documented in reports/security-report.md.
