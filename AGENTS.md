# MAIOS Project Kernel source gate

This repository is the sole source and deterministic builder for the manual
MAIOS Project Kernel package. Start from `CURRENT_STATE.md`, then read only the
source, architecture, package, test, or release files that can change the
current movement.

## Product identity

```text
living repository sources and tests
-> deterministic generated package tree
-> deterministic archive
-> explicit installer plan
-> target-owned installation
-> host discovery and behavior proof
-> maintained project reentry
```

Keep every state distinct. A passing source test or archive checksum does not
prove installation, discovery, behavioral use, or maintained reentry.

## Current owner boundaries

- This repository owns the manual self-configuring package and its builder.
- `MAIOS_CLIENT_SETUP` owns the later Form-generated route and is not an input
  to the manual 2.0.0 build.
- RepoKernel is a neutral design and generation source; its private source is
  not shipped and it does not own this package build.
- `maios_it` is a later distribution surface. Source work here grants no push,
  release, publication, runtime, or public-site authority.

The package may replace the previous product completely while preserving
source lineage and falsifiable comparison evidence. Historical package files
and the separate dirty 2.0.0 attempt are evidence, not current authority.

## Mutation rule

Before changing source or build files, identify the exact paths, expected
artifact difference, validation, and recovery. Do not modify other worktrees,
clean concurrent residue, reuse hook lifecycle files, or copy private workspace
state. Use `process/CONTAMINATION_REGISTER.json` for exact dispositions.

## Validation

```powershell
python -m unittest discover -s tests -v
python tools\build_release.py
python tools\verify_distribution.py
```

Run package installation and host/reentry acceptance separately. Preserve the
result and its evidence in `CURRENT_STATE.md` before a compact or handoff.
