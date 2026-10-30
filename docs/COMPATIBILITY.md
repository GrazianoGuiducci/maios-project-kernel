# Host compatibility

The project-local installer and helper require Python >=3.11. Qualified support covers Python 3.11–3.14 on Linux,
Windows and macOS. Newer versions are not qualified; the OS matrix does not
claim every architecture. No
third-party Python packages are required.

All hosts receive the same neutral project sources. Native profiles project the
permanent system owner and the host-adaptation competence; the latter can map
the remaining portable competences into the conventions already understood by
the current coder without forking Kernel meaning.

| Host id | Project-local skill root | Initial native projection | Global writes |
| --- | --- | --- | --- |
| `codex` | `.agents/skills` | system and all declared portable competence owners | none |
| `claude` | `.claude/skills` | system and host adaptation | none |
| `opencode` | `.opencode/skills` | system and host adaptation | none |
| `hermes` | `.hermes/skills` | system and host adaptation; explicit project trust | none |
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
| Codex | [OpenAI: Build skills](https://learn.chatgpt.com/docs/build-skills) | Repository-scoped `.agents/skills` is a native discovery root |
| Claude Code | [Anthropic: Extend Claude with skills](https://code.claude.com/docs/en/skills) | Project `.claude/skills/<name>/SKILL.md` is native |
| OpenCode | [OpenCode: Agent Skills](https://opencode.ai/docs/skills) | Project `.opencode/skills` is native; `.agents/skills` is also compatible |
| OpenClaw | [OpenClaw: Skills](https://docs.openclaw.ai/tools/skills) | Workspace `.agents/skills` is a supported project-agent root |
| Pi | [Pi coding agent: skills](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/skills.md) | A trusted project can discover `.agents/skills` |
| Hermes | [Hermes: Skills System](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills) and [configuration](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) | Project `.hermes/skills` and `.agents/skills` are native discovery roots after explicit trust |
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

Hermes discovers project `.hermes/skills/` and `.agents/skills/` in a Git
checkout. This adapter installs the system and host-adaptation entries in
`.hermes/skills/`. After reviewing the project, the operator can explicitly
trust it from that checkout:

```powershell
hermes skills trust
hermes
```

Trust is a separate host action: Hermes records trusted project directories in
the user's configuration. The installer does not grant trust or modify that
configuration. No project-local profile override is needed. Provider credentials,
sessions and other host settings remain user-owned; do not copy them into the
project. A fresh target must be a Git checkout for this native discovery route.

## 5.5.0 continuity and evidence

This version changes delivered knowledge and its source/entry relations while
retaining family 3.0.0, runtime, installer/recovery, configuration/operating
schemas, host contracts and the declared Python/OS support matrix.
The initial managed host state still selects one adapter; the deeper method
for qualifying observations does not install a receiver-scoped state store.
Shared project knowledge and an actor's actual access/use remain distinct.

The [bounded precursor observation](USE_OBSERVATION_5.5.0.md) used a supplied
filesystem adapter with Codex App Server. Native compact and continuation were
observed there; terminal execution, other hosts and general assimilation were
not established by that case. The adapter is not shipped as a new runtime.
For already evolved installations, the [updating guide](UPDATING.md) preserves
local methods and historical receipts; no automatic cross-version migration
or multi-instance synchronization is introduced.
