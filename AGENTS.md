# MAIOS Project Kernel source gate

This repository is the sole source and deterministic builder for the autonomous
MAIOS Project Kernel package. Start from `CURRENT_STATE.md`, then read only the
source, architecture, package, test, or release files that can change the
current movement.

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
- RepoKernel is a neutral design and generation source. Reviewed functions are
  translated into owner-native package organs; its private source is not
  shipped and it does not own this package build.
- `maios_it` is a later distribution surface. Source work here grants no push,
  release, publication, runtime, or public-site authority.

## Public knowledge and contribution field

A coder entering the repository can also study and evolve the public Kernel
source without installing the package.

- For Kernel study or explanation, read `knowledge/KERNEL.md` and
  `skills/maios-kernel-study/SKILL.md`.
- For a paper or rigorous article, read `research/AI_KERNEL_PAPER_FIELD.md` and
  `skills/maios-kernel-paper/SKILL.md`.
- For a human or model contribution, read `contributions/README.md` and
  `skills/maios-kernel-contribution/SKILL.md`.

These are repository-native competences. They are intentionally outside
`release/PROJECTION.json`; do not infer that opening the clone installs them in
another project or that a contribution changes the generated package. If real
use later makes package inclusion material, select and validate that product
effect explicitly.

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
