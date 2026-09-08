# Host discovery — generated project guide

The installer selects one initial host profile. Every profile receives the
same neutral Kernel and competence sources; paths and invocation names are
host mechanics rather than different Kernel meanings.

For later continuation through another instance or harness, use the
`maios-project-host-adaptation` competence and its
`references/shared-project-continuity.md`; use `maios-project-coordination`
for a material handoff or intersecting work. The shared sources can teach the
receiving assistant how to form the required connection when it is needed.
Per-instance capability state and simultaneous-write coordination are not
automatically established by installing an initial host profile.

| Host | Initial native projection |
| --- | --- |
| ChatGPT / Codex coding agent | `.agents/skills/` contains the system entry and all portable competence owners |
| Claude Code | `.claude/skills/` contains the system entry and host-adaptation competence |
| OpenCode | `.opencode/skills/` contains the system entry and host-adaptation competence; OpenCode can also discover `.agents/skills/` |
| OpenClaw | `.agents/skills/` contains the system entry and host-adaptation competence inside the workspace |
| Pi coding agent | `.agents/skills/` contains the system entry and host-adaptation competence inside a trusted project |
| DeepSeek Harness (DSH) | `.agents/skills/` contains the system entry and host-adaptation competence |
| Hermes | `.hermes/skills/` contains the system entry and host-adaptation competence |
| Generic | root instructions plus neutral competence sources under `skills/` |

## Refresh host mechanics from their owners

The installed paths are current projections, not permanent limits on later
host forms. Use the owner-qualified source for a convention that is missing,
ambiguous or likely to have changed:

| Host | Current owner source | Boundary to retain |
| --- | --- | --- |
| Codex | [OpenAI: Build skills](https://developers.openai.com/codex/skills) | `.agents/skills` is repository-scoped; discovery is still observed separately |
| Claude Code | [Anthropic: Extend Claude with skills](https://code.claude.com/docs/en/skills) | `.claude/skills` is project-scoped |
| OpenCode | [OpenCode: Agent Skills](https://opencode.ai/docs/skills) | `.opencode/skills` is native and `.agents/skills` is compatible |
| OpenClaw | [OpenClaw: Skills](https://docs.openclaw.ai/tools/skills) | `.agents/skills` is a project-agent root inside the selected workspace |
| Pi | [Pi coding agent: skills](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/skills.md) | Project skill discovery follows trust of the project |
| Hermes | [Hermes: Skills System](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills) | The active `HERMES_HOME` owns the whole profile, not only skills |
| DSH | No owner-qualified public convention source is bound by this package | Treat `.agents/skills` as a readable portable projection until native discovery is observed |
| Generic | [Agent Skills specification](https://agentskills.io) | Direct reading remains sufficient when the host has no native skill mechanism |

`maios-project-host-adaptation` lets the present coder translate the remaining
neutral startup, context and competence-formation owners into another native
form when that changes discovery or use. A capable coder can also read those
sources directly. The profile therefore provides an immediate entry without
pretending that one static table knows every current harness convention.

Hermes discovers skills from its active `HERMES_HOME`, not from an arbitrary
project `skills/` directory. Start it from the project with a project-local
home so discovery uses an isolated profile and does not change the user's
global Hermes profile:

```powershell
$env:HERMES_HOME=(Resolve-Path .\.hermes).Path
hermes
```

That environment variable selects the complete Hermes profile root, including
configuration, sessions, caches and skills. The adapter-installed
`.hermes/.gitignore` keeps Hermes-created or sensitive state outside repository
tracking while retaining the installer-owned semantic and adaptation skills.
Do not copy a global Hermes `.env` or profile into the project. Provider and
credential selection remain a separate user-owned host decision.

Projection establishes which files were installed. When it matters whether a
host discovered, read, used or resumed from them, retain the actual observation
and its evidence. `python maios.py host-status` keeps these claims separate.
`admit-host-attestation` records an observation and checks its input; use
`validate-host-attestation` when inspecting the input helps. A separate reviewer
is not required to record directly observed behavior. Recording does not
replace evidence or require every stage to be demonstrated at each entry.
