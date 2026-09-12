# MAIOS Project Kernel 4.1.1 — installable package projection

MAIOS Project Kernel gives a project and its AI coding agent shared context,
evolving competences and knowledge that carries work across sessions.

This `package/` folder is ready to install. `INSTALL.md` documents `install.py`;
`maios-project-integration` provides the package reference for the coder.
`payload/` contains the project files installed by `install.py`. `MANIFEST.json`
and `PACKAGE_INVENTORY.json` identify their source and integrity. The installer
previews changes, applies the resulting plan and records recovery information.
After installation, `START_HERE.md` is the entry for using the kernel.

Idempotent reapplication covers only this exact artifact on its unchanged
installation. It is not an in-place migration from a project installed by a
different product version; `INSTALL.md` preserves that boundary explicitly.

Running the installer and the installed helper requires Python 3.10 or later.
No third-party Python packages are required.
