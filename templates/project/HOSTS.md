# Host discovery — generated project guide

The installer selects one initial host profile. Every profile receives the
same neutral Kernel and competence sources; paths and invocation names are
host mechanics rather than different Kernel meanings.

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

`maios-project-host-adaptation` lets the present coder translate the remaining
neutral startup, context and competence-formation owners into another native
form when that changes discovery or use. A capable coder can also read those
sources directly. The profile therefore provides an immediate entry without
pretending that one static table knows every current harness convention.

Hermes discovers skills from its active `HERMES_HOME`, not from an arbitrary
project `skills/` directory. Start it from the project with a project-local
home so discovery remains additive and does not change the user's global
Hermes profile:

```powershell
$env:HERMES_HOME=(Resolve-Path .\.hermes).Path
hermes
```

The adapter-installed `.hermes/.gitignore` keeps Hermes-created configuration,
sessions, caches, and credentials outside repository tracking while retaining
the installer-owned semantic and adaptation skills. Do not copy a global
Hermes `.env` or profile into the project. Provider and credential selection
remain a separate user-owned host decision.

Projection proves installed bytes only. A fresh host must independently show
that it discovered the skill, read current state, used the relevant logic, and
could reenter from the resulting state. `python maios.py host-status` keeps
these claim levels separate. Reviewed observations can be validated and
admitted through `validate-host-attestation` and `admit-host-attestation`;
receipts do not self-certify the evidence they reference.
