# MAIOS Project Kernel 3.0.3 — installable package projection

Open this tracked `package/` folder with your coder and ask it to read `AGENTS.md` and
use `maios-project-integration`. If the target and intended change are already
clear, the coder can offer the direct project start with a concise effect and
recovery preview. A wider explanation remains available when something
material is ambiguous or you request it.

Then use `install.py` and follow `INSTALL.md`.
`payload/` is the source-bound project tree; do not copy its files manually.
`MANIFEST.json` and `PACKAGE_INVENTORY.json` bind the exact artifact, while the
installer produces an exact target plan and recovery-bearing receipt.

Idempotent reapplication covers only this exact artifact on its unchanged
installation. It is not an in-place migration from a project installed by a
different product version; `INSTALL.md` preserves that boundary explicitly.

Running the installer and the installed helper requires Python 3.10 or later.
No third-party Python packages are required.
