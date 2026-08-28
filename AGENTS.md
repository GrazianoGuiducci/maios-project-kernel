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

The current source describes the product that is built now. Version history
belongs to Git and `CHANGELOG.md`; it does not remain as a second startup,
schema, receipt or package topology inside the living tree.

## Mutation rule

Before changing source or build files, identify the exact paths, expected
artifact difference, validation, and recovery. Do not modify dirty concurrent
worktrees, reuse hook lifecycle files, or copy private workspace state.

## Validation

```powershell
python -m unittest discover -s tests -v
python tools\build_release.py
python tools\verify_distribution.py
```

Run package installation and host/reentry acceptance separately. Preserve the
result and its evidence in `CURRENT_STATE.md` before a compact or handoff.
