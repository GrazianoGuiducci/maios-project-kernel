# Host discovery — generated project guide

The installer selects one host projection:

| Host | Native skill destination |
| --- | --- |
| Codex | `.agents/skills/` contains the system entry plus new-project, existing-project and context competences |
| Claude Code | `.claude/skills/maios-project-system/SKILL.md` |
| OpenCode | `.opencode/skills/maios-project-system/SKILL.md` |
| DSH | `.agents/skills/maios-project-system/SKILL.md` |
| Hermes | `.hermes/skills/maios-project-system/SKILL.md` |
| Generic | root instructions plus neutral competence sources under `skills/` |

Codex is the first complete native competence projection. The neutral sources
for `maios-start-new-project`, `maios-start-existing-project` and
`maios-project-context` are installed for every host; the other harness
adapters currently project the permanent `maios-project-system` entry and can
be extended after the Codex behavioral vertical establishes the contract.

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
the installer-owned semantic skill. Do not copy a global Hermes `.env` or
profile into the project. Provider and credential selection remain a separate
user-owned host decision.

Projection proves installed bytes only. A fresh host must independently show
that it discovered the skill, read current state, used the relevant logic, and
could reenter from the resulting state. `python maios.py host-status` keeps
these claim levels separate. Reviewed observations can be validated and admitted
through `validate-host-attestation` and `admit-host-attestation`; receipts do not
self-certify the evidence they reference.
