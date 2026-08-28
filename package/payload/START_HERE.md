# Start here — stable system boot

This project contains MAIOS Project Kernel 3.0.0. It was installed through an
explicit package plan; installation did not configure the project or prove
that the current host has used its faculty.

This boot remains compact and stable. It restores what the Kernel is, how the
project enters it and which competences own startup, context, host adaptation,
work and learning. The changing context remains with the operator, actual
project sources, `setup/CONFIGURATION_STATE.json`, `project/CURRENT_STATE.md`
and the competences that act. A fresh reentry therefore recovers the current
field without continually rewriting the boot.

Ask the current assistant:

```text
Read START_HERE.md, determine whether this is a new or existing project, and
use the corresponding MAIOS startup competence. Explain what you understand,
then give me the first useful correctable result from what I have already said
or placed here.
```

The assistant starts from your current request, the real project files, and
`setup/CONFIGURATION_STATE.json`. A new project forms its first context; an
existing project preserves its current identity and work. The context
competence shows a useful interpretation and possibilities before requesting
non-decisive detail, then prepares the working projections needed by the
competences that will act.

If this coder uses another harness incarnation, `maios-project-host-adaptation`
connects the same neutral Kernel relation to that host's instruction, skill,
tool and reentry conventions. The coder's current knowledge of its own system
is part of that adaptation.

At first entry, the coder also checks
`.maios/kernel/PROJECT_ENTITY_PROFILE.json#environment_readiness`. It explains
and helps prepare any material missing condition—capable harness, model access,
Python, recommended version control or optional remote infrastructure—before
project implementation. The profile does not select providers, create
accounts, install global software or receive credentials by itself.

When their composition leaves a real capability gap, or concrete work exposes
a reusable causal correction, `maios-project-competence-formation` forms or
evolves the smallest project-local competence that changes the result. This is
a portable project faculty, not the private whole-kernel generator.

The canonical semantic sources are:

- `.maios/kernel/SYSTEM_KERNEL.md`;
- `.maios/kernel/FACULTY_FIELD.json`;
- `.maios/kernel/COMPOSITION_PROTOCOL.md`;
- `setup/CONFIGURATION_STATE.json`;
- `project/CURRENT_STATE.md`.

The package also includes `.maios/kernel/PROJECT_ENTITY_PROFILE.json` and
`.maios/kernel/PROJECT_META_FACULTY.json`, generated once from the accepted
neutral RepoKernel relation. They describe deferred startup and general
functional coverage, but do not create another kernel or runtime dependency.
`maios-project-system` composes them through the MAIOS-native faculty field.

`python maios.py status` checks the installed structure. `python maios.py
compose --circumstance <file.json>` can project represented package
competences, project-local competences, reachable learning and known faculty
families for a declared circumstance, but the output is not semantic selection
or proof.
`python maios.py configuration-status` distinguishes pending, accepted, stale,
and hash-linked configuration projections. `competence-status` shows separately
governed project-local competence history without claiming later assimilation.
`learning-status` shows causal learning that is immediately reachable in a
matching circumstance, while keeping persistence distinct from assimilation.
`operating-status` exposes the current project relation when durable state or
reentry needs it. After a real result is inspected, `validate-resultant` and
`apply-resultant` can couple that terminal readback to configuration, evolution,
learning, projections, and reentry without granting an external effect. A
causal learning delta can enter the next matching movement immediately; later
non-identical behavior is still needed to support assimilation.

Project-local, reversible configuration is allowed when you asked to initialize
or use the project. An external, public, destructive, credentialed, or runtime
effect remains a separate exact decision. Current intent and verified reality
outrank stored continuity on every reentry.
