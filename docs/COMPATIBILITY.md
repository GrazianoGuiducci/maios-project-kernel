# Host compatibility

The project-local installer and helper require Python 3.10 or later. No
third-party Python packages are required.

All hosts receive the same neutral project sources. Native profiles project the
permanent system owner and the host-adaptation competence; the latter can map
the remaining portable competences into the conventions already understood by
the current coder without forking Kernel meaning.

| Host id | Project-local skill root | Initial native projection | Global writes |
| --- | --- | --- | --- |
| `codex` | `.agents/skills` | system, startup, context, formation, and host adaptation | none |
| `claude` | `.claude/skills` | system and host adaptation | none |
| `opencode` | `.opencode/skills` | system and host adaptation | none |
| `hermes` | `.hermes/skills` | system and host adaptation; use project-local `HERMES_HOME=.hermes` | none |
| `openclaw` | `.agents/skills` | system and host adaptation | none |
| `pi` | `.agents/skills` | system and host adaptation | none |
| `dsh` | `.agents/skills` | system and host adaptation | none |
| `generic` | host-selected | root instructions and neutral `skills/` sources | none |

The selected adapter is written into `.maios/state/HOST_STATE.json` during
installation. Discovery, state reading, semantic use, an observable result, and
maintained reentry remain `unverified` until observed independently on that host.
The package does not select a model, provider, plugin, service, credential, or
network policy.

The path table is an installation map, not a semantic taxonomy. A capable coder
may read `START_HERE.md`, `HOSTS.md`, and the neutral `skills/` tree, then use
`maios-project-host-adaptation` to create the smallest faithful native
incarnation its harness requires.

Hermes does not natively scan an arbitrary project `skills/` folder. Its
adapter therefore installs the same semantic owner in a project-local Hermes
home. The caller explicitly selects that home for the process; the package
does not modify or copy the global Hermes profile.
