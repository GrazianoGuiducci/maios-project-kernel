# MAIOS Project Kernel source gate

This repository is the sole source and deterministic builder for the autonomous
MAIOS Project Kernel package. Start from `CURRENT_STATE.md`, then read only the
source, architecture, package, test, or release files that can change the
current movement.

Use `README.md` as the repository homepage and reading map. The ready-to-install
distribution is in `package/`; its `INSTALL.md` documents the installer and
`maios-project-integration` supplies package-specific knowledge. The installed
`START_HERE.md` is the entry for project work.

## Product identity

```text
living repository sources and tests
-> deterministic generated package tree
-> explicit installer plan
-> target-owned installation
-> host discovery and behavior proof
-> maintained project reentry
```

Keep every state distinct. A passing source test or package inventory does not
prove installation, discovery, behavioral use, or maintained reentry.

## Current owner boundaries

- This repository owns the autonomous self-configuring package and its builder.
- `MAIOS_CLIENT_SETUP` owns the later Form-generated route. It will preconfigure
  the same Kernel family but is not an input to this autonomous build.
- Exported generation plans supply selected methods. This repository owns
  their product integration and build; the private production compiler is not
  required for ordinary builds or installation. See docs/GENERATED_KERNEL_BUILD.md.
- `maios_it` is a later distribution surface. Source work here grants no push,
  release, publication, runtime, or public-site authority.

## Public knowledge, testing and contribution field

A coder entering the repository can study and evolve the public Kernel source
without installing the package. Real testers are also useful source evidence:
first impressions can reveal unclear entry, avoidable latency, missing context,
unexpected strengths or possibilities that maintainers no longer see as easily.

- For Kernel study or explanation, read `knowledge/KERNEL.md` and
  `skills/maios-kernel-study/SKILL.md`.
- For a human or model contribution, read `CONTRIBUTING.md`,
  `contributions/README.md` and `skills/maios-kernel-contribution/SKILL.md`.
- For real-use observations, prepare an Evolution Feedback using
  `.github/ISSUE_TEMPLATE/evolution-feedback.md`.

A coder may prepare feedback from an operator's real session, but public
submission requires the operator's consent. Remove private project material,
credentials, personal data, private logs and hidden runtime state. Use a GitHub
Issue for observed feedback; use a fork and focused Pull Request for a concrete
source correction. Do not infer direct write authority over upstream `main`.

During active use, `source-contact-status` indicates when ordinary upstream
contact is due; a material current problem can make an earlier check useful.
The method is owned by [UPDATE_CONTINUITY](kernel/UPDATE_CONTINUITY.md).
Source contact is read-only and non-blocking, without a background process or
an implied external effect. New upstream material is a possibility to
understand and propose, not an automatic update.

These public study/contribution competences are repository-native. They are
intentionally outside `release/PROJECTION.json`; do not infer that opening the
clone installs them in another project or that a contribution changes the
generated package. If real use later makes package inclusion material, select
and validate that product effect explicitly.

The current source describes the product that is built now. Version history
belongs to Git and `CHANGELOG.md`; it does not remain as a second startup,
schema, receipt or package topology inside the living tree.

## Mutation rule

Before changing source or build files, identify the exact paths, expected
artifact difference, validation, and recovery. Do not modify dirty concurrent
worktrees, reuse hook lifecycle files, or copy private workspace state.

For a contribution, preserve its source relation, expected or observed
resultant, causal readback, invalidator, reentry condition, and package
disposition. Human and AI contributors enter through the same relation;
identity does not establish truth or effect authority.

## Validation

```powershell
python -m unittest discover -s tests -v
python tools\build_release.py
python tools\verify_distribution.py
```

Run package installation and host/reentry acceptance separately. Preserve the
result and its evidence in `CURRENT_STATE.md` before a compact or handoff.
