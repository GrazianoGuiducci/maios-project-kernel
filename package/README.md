# MAIOS Project Kernel 4.5.0 — installable package projection

MAIOS Project Kernel brings an AI agent living context, evolving competences
and knowledge that carries work across sessions. Its activity can reform its
own knowledge and organization. Inquiry, domain work and projects can all
supply the context; project initialization is a competence to use when needed.

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
