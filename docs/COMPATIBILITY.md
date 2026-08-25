# Host compatibility

All hosts receive the same project and semantic owner. Adapters only place that
owner in a native project-local discovery path.

| Host id | Native projection | Global writes |
| --- | --- | --- |
| `codex` | `.agents/skills/maios-project-system/SKILL.md` | none |
| `claude` | `.claude/skills/maios-project-system/SKILL.md` | none |
| `opencode` | `.opencode/skills/maios-project-system/SKILL.md` | none |
| `dsh` | `.agents/skills/maios-project-system/SKILL.md` | none |
| `hermes` | `.hermes/skills/maios-project-system/SKILL.md`; launch with project-local `HERMES_HOME=.hermes` | none |
| `generic` | root instructions and canonical `skills/` owner | none |

The selected adapter is written into `.maios/state/HOST_STATE.json` during
installation. Discovery, state reading, semantic use, an observable result, and
maintained reentry remain `unverified` until observed independently on that host.
The package does not select a model, provider, plugin, service, credential, or
network policy.

Hermes does not natively scan an arbitrary project `skills/` folder. Its
adapter therefore installs the same semantic owner in a project-local Hermes
home. The caller explicitly selects that home for the process; the package
does not modify or copy the global Hermes profile.
