# MAIOS Project Kernel 5.1.0

MAIOS Project Kernel supplies an evolving operating kernel for an AI agent:
knowledge and methods for understanding, acting, forming competences and
continuing from useful experience. Version 5.1.0 makes competence participation
more legible and makes the autonomous receiver's ability to qualify its own
operating context explicit. These changes use the permanent system entry and
existing competence formation.

These notes describe the product source and distribution content. Publication
and execution evidence belong to the exact Git revision, CI run and assets;
the presence of these notes does not establish a tag or published release.

## A trace the person can read and correct

The [system competence](../skills/maios-project-system/SKILL.md#make-competence-participation-legible)
instructs the receiving agent to close a substantive response with a compact
trace of the competences it materially understands as having participated.
Their contribution, useful continuation or an emerged possibility can accompany
the names when that helps the person understand or continue the work.

This is situated, correctable self-attribution by the receiver. Reading or
having a skill available does not establish participation. The trace is not
chain-of-thought evidence, a registry, a fixed stack or a prescription for the
next turn. The permanent [installed entry template](../templates/project/AGENTS.md)
carries the minimum invocation; the system owns its meaning and limits.

## The receiver can form what its context needs

An autonomous receiver does not presume the creator's qualification, context,
topology or means. When a durable capacity or its continuation is materially
missing, the system invokes the existing
[competence-formation knowledge](../skills/maios-project-competence-formation/SKILL.md)
to reuse, deepen, compose or form what is useful. An adequate existing owner can
carry the change directly.

When formation is needed, it supplies the minimum owner, working knowledge and
native entry or reentry needed in that context. A competence, sub-kernel or
continuation surface is a situated possibility, not an obligatory set of
artifacts. Local learning remains owned by the receiver. Formation does not
invent tools, accounts, credentials, network access or authority. The practical
depth remains in the existing formation body, generative seed and references;
no new skill, controller or subsystem is added.

## Context is required; an interview is discretionary

The autonomous lane of the
[family source contract](../kernel/PROJECT_KERNEL_FAMILY_CONTRACT.json)
now states `startup_context_requirement=required` and
`startup_interview=discretionary`. This converges the source on the semantics
already supplied by the autonomous entry contract and installed payload in
5.0.0. It is not a new runtime configuration flow.

The Form lane remains `preconfigured_from_accepted_form_context` with
`startup_interview=complete`. Historical RepoKernel inputs and receipts retain
their original meaning and hashes. This source update does not modify a Form
deployment, site or existing installation.

## Compatibility and support

This is a minor product version: the trace and receiver qualification add
explicit operating and interaction capabilities; the family-source correction
clarifies an existing delivered contract. **Project Kernel
family 3.0.0** is unchanged. Runtime, installer/recovery, state schemas and host
contracts retain their compatibility.

The technical minimum remains **Python >=3.11**. Qualified support remains
**Python 3.11–3.14 on Linux, Windows and macOS**, exercised by the 12-job matrix:
Ubuntu and Windows latest plus macOS 15 Intel, each with four Python versions.
This does not qualify every processor architecture or later Python version.

The adapter set remains `generic`, `codex`, `claude`, `opencode`, `hermes`,
`openclaw`, `pi` and `dsh`, with the same native paths and trust boundaries.
[Compatibility](COMPATIBILITY.md) retains their individual evidence limits.
No host activation or observed model behavior follows from profile availability.

Same-artifact idempotence is unchanged. A new version is not an automatic
migration: preserve locally evolved knowledge through
[update continuity](../kernel/UPDATE_CONTINUITY.md) and follow
[installation and recovery](INSTALLATION.md) for the selected target.

## Distribution and evidence

The ordinary builder reads current product sources and generates the package,
manifest and inventory. The full suite checks source contracts, installation,
recovery and state behavior; two identical builds, active links and distribution
verification bind the generated content. The
[workflow](../.github/workflows/verify.yml) exercises the complete OS/Python
matrix and retains candidate archives.

The archive contract is:

- `maios-project-kernel-5.1.0.zip`
- `maios-project-kernel-5.1.0.sha256`, containing the ZIP's SHA-256 and filename.

Fixed member metadata and uncompressed ZIP entries make the archive reproducible
across the qualified runners. Compare the inner ZIP digest, not the digest of a
CI artifact container. [Build instructions](GENERATED_KERNEL_BUILD.md) describe
how to reproduce these bytes without publishing a release.

Installed, discovered, exercised and assimilated are distinct claims. Tests
exercise executable contracts; readback checks the delivered instructions and
their reachable depth. Neither proves that a receiving LLM has assimilated the
competence trace or endogenous qualification. Evidence for 5.0.0 and for an
earlier candidate remains bound to those identities.
