---
name: maios-project-integration
description: Package knowledge for installing MAIOS Project Kernel: purpose, requirements, installer modes, coding host profiles, verification, recovery and the installed entry.
---

# MAIOS Project Integration

MAIOS Project Kernel gives a project and its AI coding agent shared context,
competences and knowledge that continues across sessions. The ready-to-install
distribution is the repository's `package/` folder.

## Installation reference

- `INSTALL.md` documents the `install.py` commands, conflicts and recovery.
- `MANIFEST.json` identifies the product and requirements;
  `PACKAGE_INVENTORY.json` is the file inventory verified by the installer.
- `adapters/ADAPTERS.json` lists coding hosts and their native entry paths.
- Python 3.10 or later runs the installer and installed helpers, using only
  the standard library.

The installer takes a target folder and host. Its default `--mode auto` derives
folder handling and preserves the mode of an unchanged same-package installation.
An explicit mode is optional. `new_repository` accepts
an absent or empty folder. `existing_repository` adds files to a non-empty
folder, preserves identical files and reports conflicting content. These modes
describe filesystem handling; project intent comes from the actual work.

`preview` produces the exact file plan and `apply` applies it. Plan files and
optional CLI receipt outputs belong outside the package, source checkout and
target; the examples use the system temporary directory. Installation affects
project-local paths, including the selected host's entry.

Verification, interrupted-install recovery and uninstall are documented in
`INSTALL.md`. Reapplying the same artifact to its unchanged installation is
idempotent. A different version requires an update comparison with local work;
the installer does not implement cross-version migration.

## Installed kernel

`START_HERE.md` introduces the kernel and the project's current context.
The installed configuration helpers maintain state and its readable views.
`integration_handoff` is an optional configuration field for useful installation
context. `.maios/kernel/UPDATE_CONTINUITY.md` explains how the saved installation
baseline, local learning and later upstream changes relate.
