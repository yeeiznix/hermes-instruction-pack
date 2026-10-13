# Hermes Adapter

Integration with **Hermes Agent v0.21.0** (verified on this machine: `~/.hermes/hermes-agent`, commit `05f548f3`, venv Python 3.13.13).

## Mechanisms used (official only)

| Surface | Use by this pack |
|---|---|
| `agent.personalities` (dict name→prompt) | Registers `hip-rat`, `hip-eni`, `hip-seraph`, `hip-axiom` |
| `agent.instructions` (list of file paths) | Optional `--with-instructions` appends core module paths |
| `hermes config` semantics | Adapter edits the same YAML the CLI owns; backup always taken first |
| Skills (`~/.hermes/skills/*/SKILL.md`) | Not required by the pack; available for future packaging |

Never touched: `agent.system_prompt`, `prefill_messages_file`, `display.personality`, `.env`, `auth.json`.

## Commands

```bash
cd ~/hermes-instruction-pack
export PYTHONPATH=src

python3 -m hermes_instruction_pack.cli adapter check          # compatibility report (exit 0 iff compatible)
python3 -m hermes_instruction_pack.cli adapter install --dry-run
python3 -m hermes_instruction_pack.cli adapter install        # writes config after backup
python3 -m hermes_instruction_pack.cli adapter install --with-instructions
python3 -m hermes_instruction_pack.cli adapter uninstall      # remove hip-* personalities
python3 -m hermes_instruction_pack.cli adapter rollback       # restore last backup
```

## Safety properties

- Timestamped backup in `adapters/hermes/backups/config.yaml.bak-hip-<ts>` before any write.
- `install-state.yaml` records what was changed for rollback.
- Dry-run prints the full plan without touching the config.
- No secrets printed; config contents are never dumped to stdout.
- Personality names are prefixed `hip-` to avoid clobbering Hermes built-ins.

## Activate a persona inside Hermes

After install, use Hermes' own selection (config or slash command):

```yaml
# ~/.hermes/config.yaml
display:
  personality: hip-rat    # or hip-eni / hip-seraph / hip-axiom / none
```

Or in a Hermes session: `/personality hip-rat`.

## Rollback

`hip adapter rollback` restores the most recent pack backup and retires `install-state.yaml`.
Multiple backups accumulate; older ones can be restored manually by copying over `config.yaml`.
