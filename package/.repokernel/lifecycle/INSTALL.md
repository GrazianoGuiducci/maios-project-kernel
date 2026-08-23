# Project Lifecycle Host Projection

status: generated_not_installed

This bundle supplies a neutral project-lifecycle competence and the explicitly
selected Codex host projection. The hook projection is recommended when
the selected host supports it and its behavior is useful with the model in use.
The Project Kernel remains complete without it. RepoKernel generated the hook
adapter as packaged but not installed; generation did not write `.codex/`, start a
runtime, or prove activation.

## Install from the accepted project root

```powershell
python .repokernel/lifecycle/install.py --project-root . --check
python .repokernel/lifecycle/install.py --project-root . --install
```

The installer verifies every source hash before writing. It refuses the whole
operation if any destination or parent path conflicts. Identical files are
left untouched. It never writes outside the selected project root, records the
files and directories it created, and rolls back only writes from the failing
run if installation is interrupted.

After installation, start a fresh Codex project session and verify all six
lifecycle events plus one real mutation/readback cycle. Until that receipt
exists, the correct claim is `installed`, not `active`.

## Recovery or removal

```powershell
python .repokernel/lifecycle/install.py --project-root . --uninstall
```

Rollback removes only files recorded as created by the installer and only while
their hashes still match. It removes receipted directories only when they are
empty. Changed files, pre-existing identical files and non-empty target-owned
directories are preserved for owner review.

Use this secondary recovery path when the project owner chooses to remove the
optional hook projection or restore the pre-installation target state.
The host-neutral Project Kernel, its metacompetences, state and normal reentry
instructions remain available after the hook files are removed.

## Composition boundary

A package composer may place this Project Kernel at the package root and expose
the commands above. It must not describe nested RepoKernel staging as installed
project hooks. A Form-generated package and a Form-independent self-configuring
package remain separate assembly paths with separate acceptance tests.
