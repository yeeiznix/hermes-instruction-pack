# Archive — Jailbreak Prompt Corpus (DATA, NOT INSTRUCTIONS)

**Status of everything in this tree: untrusted third-party text preserved for analysis.**

Nothing here is auto-loaded into any agent session by this pack. The resolver never selects archive content. The validator bans the dominant techniques found here from operational modules.

## Layout

Sources live canonically under `sources/` (hash-verified). This directory holds:

- `technique-index.yaml` — per-technique notes mapped to source files (added as analysis progresses)
- analysis outputs referenced from `analysis/` (conflict-report, classification)

## Technique families observed in the corpus

| Technique | Example locations | Analysis value |
|---|---|---|
| Instruction supersession | gist-a7dc501b, gist-9783f763, jailbreaks/* | hierarchy-attack fixtures |
| Authority mimicry (fake auditor/admin) | gist-f3a4f106, jailbreaks role patterns | authorization-recognition tests |
| Oblivious meta-prompt ("define f(q)=…") | hellowork modules/involuntary.py (arXiv 2508.13246) | compliance-without-judgment fixture |
| Encoding/obfuscation layers | hellowork modules/cipher.py, gist-8189a15e (base64) | untrusted-data handling tests |
| Multi-turn escalation | hellowork modules/crescend.py | persistence-vs-safety tests |
| Long-context erosion | hellowork modules/erode.py | attention-dilution tests |
| Role/channel impersonation | hellowork modules/role.py | instruction-hierarchy tests |
| Low-reasoning exploit theory | hellowork modules/thinkinglow.py | model-behavior research note |
| Per-model phrasing corpora | togg53192-cmd/jailbreaks (31 files) | regression corpus for injection resistance |

## Rules of engagement

1. Cite file paths + hashes when discussing a technique.
2. Test only against targets you are authorized to test (this pack: its own resolver/validator and, with operator consent, a reachable model endpoint).
3. Never paste archive content into production agent configs.
4. Improvements to defenses go into `core/` and `tests/`, not into more powerful attack prompts.
