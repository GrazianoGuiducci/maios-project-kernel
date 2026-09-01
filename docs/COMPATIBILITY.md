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

## Current convention sources

These links let a coder refresh host mechanics without turning current paths
into permanent Kernel limits. They are documentation sources, not runtime or
build dependencies.

| Host | Owner-qualified reference | Current package relation |
| --- | --- | --- |
| Codex | [OpenAI: Build skills](https://developers.openai.com/codex/skills) | Repository-scoped `.agents/skills` is a native discovery root |
| Claude Code | [Anthropic: Extend Claude with skills](https://code.claude.com/docs/en/skills) | Project `.claude/skills/<name>/SKILL.md` is native |
| OpenCode | [OpenCode: Agent Skills](https://opencode.ai/docs/skills) | Project `.opencode/skills` is native; `.agents/skills` is also compatible |
| OpenClaw | [OpenClaw: Skills](https://docs.openclaw.ai/tools/skills) | Workspace `.agents/skills` is a supported project-agent root |
| Pi | [Pi coding agent: skills](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/skills.md) | A trusted project can discover `.agents/skills` |
| Hermes | [Hermes: Skills System](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills) and [configuration](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) | Skills live under the active `HERMES_HOME`; this package supplies a project-local profile root |
| DSH | No owner-qualified public convention source is bound by this package | `.agents/skills` is a readable portable projection; native discovery remains unverified |
| Generic | [Agent Skills specification](https://agentskills.io) | Neutral sources remain directly readable even without native discovery |

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
home. The caller explicitly selects that `HERMES_HOME` for the process. This
selects a complete project-local Hermes profile boundary, including skills,
configuration, sessions and caches; `.hermes/.gitignore` keeps generated or
sensitive profile state out of project tracking. The package does not modify or
copy the global Hermes profile.
