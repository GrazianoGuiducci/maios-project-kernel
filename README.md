# MAIOS Project Kernel

MAIOS Project Kernel gives a project and its AI coding agent a shared operating
kernel: knowledge and methods for understanding the situation, doing useful
work, developing competences and continuing as the project changes.

The project retains the reasons behind decisions, the sources that support
them and the knowledge acquired through work. A later agent can recover that
context and continue from it without treating another instance's experience as
its own personal memory.

Product version: **[4.1.1](VERSION.md)** · Project Kernel family: **3.0.0** ·
Python **3.10 or later** · [MIT License](LICENSE)

[Versione italiana](README.it.md)

## What it makes possible

- Understand a new or existing project through its actual sources, intent,
  constraints and open possibilities.
- Bring in, combine or form the competences useful to the work. Intent,
  knowledge, successful results and new possibilities can all change what is
  worth developing; learning does not require a failure first.
- Keep reasons, decisions and consequences connected, and return reusable
  learning to the methods that should change.
- Continue across sessions and cooperating agents through knowledge owned by
  the project, preserving current work and the reasons for its direction.

KA keeps the field of possibilities open; FDLA corrects distortions while work
forms; Meta_Skill recognizes, composes and develops competences. These functions
act together through the agent and the project's sources. The
[Kernel guide](knowledge/KERNEL.md) explains their meaning and operation.

## Start with your project

Clone or download this repository and open its [`package/`](package/) folder
with your coding agent. The installable distribution is already included;
you do not need to run a build to use it. Ask the agent:

```text
Inside package/, read AGENTS.md and use maios-project-integration.
I want to use MAIOS in [target project]. Understand the project and my current intent, explain the
useful contribution you can make, and show the installation changes and
recovery before applying them. Use what is already clear; ask only for missing
information that changes the integration.
```

Opening the folder does not install anything. The agent identifies the target
and host, prepares missing requirements, previews the exact changes, and applies
the accepted plan. After installation, open the target project and ask it to
read `START_HERE.md`, then continue with your actual work.

**New project:** the installer accepts an absent or empty target. The agent
forms enough shared context to begin useful work and develops it along the way.

**Existing project:** the agent reads existing instructions, sources and work.
The installer preserves identical files, adds missing ones and refuses
conflicting content for explicit reconciliation.

The installer and local helpers require Python 3.10 or later and no third-party
Python packages. See [installation and recovery](docs/INSTALLATION.md) for
preview/apply commands, conflict handling and uninstall; see the
[usage guide](docs/USAGE.md) for integration, competences and daily operation.

## Work, learn and return

The installed agent uses the project's context and relevant competences to form
a result. New knowledge, a successful approach, a possibility or a correction
can then change the methods used next. The project keeps the useful reasons
and continuation rather than requiring the whole conversation to be replayed.

`START_HERE.md` is the stable entry. Living competence bodies own methods;
project state and knowledge carry the changing context. Existing local helpers
include `status`, `configuration-status`, `competence-status`, `learning-status`
and `operating-status`; the [usage guide](docs/USAGE.md#project-local-operation)
shows how to invoke them.

Updating a package is distinct from evolving a project's knowledge. Reapplying
the exact artifact to an unchanged installation is idempotent; a different
version is not an automatic migration. The
[update-continuity method](kernel/UPDATE_CONTINUITY.md) relates the installation
baseline, local evolution and a proposed update.

## Test, feedback and updates

Real testers are valuable to the Kernel's evolution. A first-use impression can
show unclear entry, unnecessary latency, missing context, unexpected strengths
or a new possibility even when no technical bug exists.

The installed Project Kernel already keeps a light source contact: during
active use, an upstream check becomes pertinent when no attempt is recorded or
roughly seven days have elapsed since the last attempt, and sooner when a
current problem may already have been corrected upstream. The check is
read-only and non-blocking; a newer source is a possibility to understand, not
an automatic update. See
[`kernel/UPDATE_CONTINUITY.md`](kernel/UPDATE_CONTINUITY.md#keep-a-light-source-contact).

When real use produces an informative observation, ask your coder to prepare an
**Evolution Feedback**. The coder should show you the public-safe feedback and
ask for your consent before submitting it. Use a GitHub Issue for experience,
friction, questions, unexpected success or a possible improvement; use a fork
and focused Pull Request for a concrete source correction. Testers do not need
and should not receive direct write access to upstream `main` merely to
contribute.

See [CONTRIBUTING.md](CONTRIBUTING.md) and the
[GitHub Evolution Feedback template](.github/ISSUE_TEMPLATE/evolution-feedback.md).
Feedback is evidence for maintainers, not automatic authority to change the
Kernel or the tester's project.

## Coding hosts and evidence

The package provides profiles for `codex`, `claude`, `opencode`, `hermes`,
`openclaw`, `pi`, `dsh` and `generic`. The
[compatibility guide](docs/COMPATIBILITY.md) identifies their installed paths
and discovery conditions. An available profile does not establish observed
use by every host or model.

Source tests and distribution verification cover package integrity, installer
and recovery mechanics, routing and local state contracts. They do not prove
that a receiving model understands, uses or assimilates the methods. See the
[4.1.1 evidence](docs/RELEASE_4.1.1_EVIDENCE.md) for dated observations and
[release notes](docs/RELEASE_4.1.1.md) for the version's changes.

## Study, contribute or build

You can study and improve the public source without installing the package.
Open the repository root with your agent and ask it to read `AGENTS.md` and use
`maios-kernel-study`. People and AI models can contribute methods, knowledge,
questions, evidence and code through the [contribution guide](CONTRIBUTING.md).
The repository's [maios-kernel-contribution](skills/maios-kernel-contribution/SKILL.md)
competence helps turn that work into a contribution grounded in its sources.

| Your next step | Documentation |
| --- | --- |
| Use and maintain a project | [Usage](docs/USAGE.md) · [Installation](docs/INSTALLATION.md) |
| Understand the Kernel | [Knowledge](knowledge/KERNEL.md) · [Architecture](docs/ARCHITECTURE.md) |
| Send real-use feedback | [Contributing](CONTRIBUTING.md) · [Evolution Feedback template](.github/ISSUE_TEMPLATE/evolution-feedback.md) |
| Work on this repository | [Documentation map](docs/README.md) · [Build](docs/GENERATED_KERNEL_BUILD.md) · [Provenance](docs/PROVENANCE.md) |
| Explore the research | [System Semantic Kernel working paper](https://github.com/GrazianoGuiducci/maios-ssk-paper), a separate academic corpus |
| Follow changes | [Changelog](CHANGELOG.md) · [Current source state](CURRENT_STATE.md) |

The repository owns the product source. `package/` is its generated installable
distribution; do not edit it directly. Public source changes and renewal of
exported method bodies follow the distinct paths in the
[build guide](docs/GENERATED_KERNEL_BUILD.md).

Software and documentation are under the [MIT License](LICENSE). See
[third-party notices](THIRD_PARTY_NOTICES.md) and [names and trademarks](TRADEMARKS.md).
