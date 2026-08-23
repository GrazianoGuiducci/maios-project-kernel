# Changelog

All notable changes to the public distribution are recorded here.

## 1.5.0 - 2026-08-23

- Added DeepSeek Harness (DSH) as a first-class host adapter for both deferred
  self-configuration and context-configured Project Kernels.
- Added `DSH_SETUP.md`, a DSH activation receipt, and portable skill discovery
  through `.agents/skills/` without requiring plugins, hooks, provider, model,
  or global DSH configuration.
- Kept DSH identity separate from TM13, RepoKernel, and the generated Project
  Kernel, and kept packaged, discovered, composed, and exercised states
  distinct.
- Corrected the setup interviewer skill identity so DSH can discover both
  `maios-setup-interviewer` and `operate-maios-project-kernel`.
- Revalidated the deterministic 66-member source archive; fresh DSH behavioral
  activation remains a separate host test.

## 1.4.0 - 2026-08-23

- Added an optional Codex project-lifecycle projection with six source-bound
  hook files.
- Kept the projection `packaged_not_installed`; extracting the package does not
  create `.codex/` or change host configuration.
- Added a read-only preflight, conflict refusal, explicit owner installation,
  installation receipt, idempotent reinstallation, and bounded uninstall.
- Preserved the complete host-neutral Project Kernel when the optional hooks
  are not installed or are removed.
- Revalidated the deterministic 64-member source archive and kept RepoKernel
  compiler source outside the distribution.

## 1.3.0 - 2026-08-14

- Composed the generated Project Kernel, project meta-faculty, local faculty
  router, and host-native discovery adapters into the self-configuring package.
- Added a typed evolution contract that distinguishes case memory, competence,
  skill, function, and meta-evolution.
- Connected initial orientation to a first useful proof and a correctable
  product or service hypothesis.
- Bounded setup latency while preserving explicit owner review of project
  truth.
- Made Project Kernel loading progressive so context is opened as the active
  decision requires it.
- Added the first public, inspectable GitHub distribution with MIT licensing,
  provenance notes, deterministic release building, and integrity checks.

## 1.2.2 - 2026-08-12

- Added an immutable package inventory with byte counts and SHA-256 hashes.
- Strengthened archive path safety, entity-profile bindings, and deterministic
  build validation.

## 1.2.1 - 2026-08-12

- Reworked first use for people who do not already know what to build.
- Made the assistant begin from the person's work, problem, or desired result
  and return a correctable understanding before deeper configuration.
- Clarified setup states and host evidence for novice-facing use.

## 1.2.0 - 2026-08-12

- Added the Project Kernel first packet and durable current-state entry.
- Added local faculty routing and made the setup operational after extraction.
- Tightened host entry documents and state continuity.

## 1.1.0 - 2026-08-12

- Added host guides and discovery adapters for Codex, Claude Code, OpenCode,
  and Hermes.
- Added host activation receipts, the MAIOS start kernel, and the axiomatic
  resultant kernel.
- Completed the first end-to-end delivery structure.

## 1.0.0 - 2026-08-11

- Created the deferred startup interview, setup contract, configuration state,
  project brief, source manifest, and deterministic package builder.
- Established the new-project-only installation boundary.
