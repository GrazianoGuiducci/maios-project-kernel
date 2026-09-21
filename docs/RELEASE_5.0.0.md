# MAIOS Project Kernel 5.0.0

MAIOS Project Kernel supplies an evolving operating kernel to an AI agent:
knowledge, competence formation and continuity for inquiry, domain work and
projects. The product version is 5.0.0; Project Kernel family 3.0.0 is unchanged.
These notes describe the release content. Publication identity and execution
results are read from the selected Git commit, CI run and distribution assets.

## Operating kernel and competence formation

The generative startup seed connects the current task to competence composition,
the resulting work and learning returned to the owner that should act differently.
It separates changing context from durable capability and makes formation itself
capable of learning. Existing general competences and consequence-aware reasoning
remain reachable through the system entry. See the
[seed](../skills/maios-project-competence-formation/references/generative-startup-seed.md)
and the [Kernel guide](../knowledge/KERNEL.md).

Current native owners directly determine the build. Explicit empty relations,
current possibility reconciliation, terminal-state binding, separate current and
deep integrity diagnostics, portable paths and invocation-owned build recovery
carry the completion developed after 4.5.0. Retained generation plans are optional
compatibility inputs, not hidden production dependencies.

## Support and compatibility

Installation and local helpers require **Python >=3.11**, using the standard
library. Qualified support covers **3.11, 3.12, 3.13 and 3.14** on **Linux,
Windows and macOS**. Newer Python versions are not implicitly supported. The
blocking matrix is Ubuntu and Windows latest plus macOS 15 Intel, each with all
four Python versions; this does not qualify every processor architecture.

Dropping Python 3.10 is the breaking support change behind the major version.
Family 3.0.0, existing state, learning and receipt contracts remain unchanged.
The conservative Windows reparse implementation still works on Python 3.11.
Idempotence applies to the same artifact on an unchanged installation; there is
no automatic in-place migration across product versions. Follow
[installation and recovery](INSTALLATION.md) and the target-owned
[update-continuity method](../kernel/UPDATE_CONTINUITY.md).

## Receiving hosts and public entry

Hermes uses project-native `.hermes/skills` / `.agents/skills` discovery in a
Git checkout after explicit `hermes skills trust`. The adapter projects skills,
without creating a whole project-local host profile or granting trust. Codex
retains id `codex` and its repository `.agents/skills` entries. Generic receiver
mapping stays open to future hosts; DSH native discovery remains unverified.
See the owner references and evidence boundaries in [compatibility](COMPATIBILITY.md).

The English and Italian READMEs explain the product, its useful consequences,
work and learning, and one concrete example before installation mechanics.
Public source describes downstream configuration and distribution by function.

## Distribution and proof

The real builder generates the tracked package, source-tree identity, manifest
and inventory. The workflow runs the full suite, checks active local document
links and anchors, builds twice with a clean package diff, verifies distribution,
and retains a deterministic archive from each of the 12 OS/Python jobs.
Test-only Markdown parsing dependencies are separate from the product runtime.

The public asset contract is:

- `maios-project-kernel-5.0.0.zip`
- `maios-project-kernel-5.0.0.sha256`, binding that ZIP's SHA-256

Archive metadata and uncompressed members have fixed bytes independent of runner
timestamps or compression-library versions. Compare the internal ZIP digest
across all jobs; an artifact container's digest is a different identity.
[Build instructions](GENERATED_KERNEL_BUILD.md) describe reproduction and
[the workflow](../.github/workflows/verify.yml) defines the blocking checks.

Source, projection, installation, host discovery and semantic use have distinct
evidence. A green suite or an available profile does not establish that a
receiving model understands, uses or assimilates the kernel.
