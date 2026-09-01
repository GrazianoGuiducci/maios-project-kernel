# Installation

## Open the package

Clone the repository and open its tracked `package/` directory with
the coder. `PACKAGE_INVENTORY.json` binds every generated package path, byte
count and SHA-256 before the installer plans a target transition.

The installer and the installed `maios.py` helper require Python 3.10 or later
and use only the Python standard library.

## Preview and apply

Opening the repository does not install or execute the package. From
`package/`:

```powershell
python install.py preview --target C:\Projects\MyProject --mode new_repository --host codex --plan-out install-plan.json
python install.py apply --plan install-plan.json
```

`new_repository` requires an absent or empty target and promotes a complete
adjacent staging directory atomically. `existing_repository` inventories every
destination, preserves identical files, creates missing files, and refuses
divergent or unsafe paths. Apply recomputes the target and package identity and
refuses a stale plan. Existing-project apply writes a `PENDING` journal before
the first file transition. After a process or machine interruption, run
`python install.py recover-pending --target <target>` from `package/`; changed
target bytes are preserved and reported.

Before planning, the installer verifies every distribution file against
`PACKAGE_INVENTORY.json` and refuses missing, changed, symlinked or untracked
files. Its entry disables local Python bytecode generation so invoking the
installer does not contaminate the package projection with `__pycache__`.

## Reinstallation and version migration

Reapplying the exact same artifact to its unchanged installation is
idempotent. That property is not a cross-version upgrade claim. This package
does not implement an in-place migration from a project installed by another
product version, including 3.0.1 to 3.0.2 or 3.0.2 to 3.0.3. Preserve the
existing target and its project-evolved files; if migration becomes necessary,
treat it as a separate target-owned movement with an explicit inventory,
reconciliation, effect, and recovery relation.

Supported host ids are `generic`, `codex`, `claude`, `opencode`, `hermes`,
`openclaw`, `pi`, and `dsh`.

For Hermes, run the installed project with its adapter-owned project-local
home so the host can discover the semantic skill without changing global
Hermes state:

```powershell
Set-Location C:\Projects\MyProject
$env:HERMES_HOME=(Resolve-Path .\.hermes).Path
hermes
```

Use a user-selected provider credential mechanism; do not copy a global Hermes
profile or `.env` into the project.

## Verify and uninstall

```powershell
python C:\Projects\MyProject\.maios\installer\installer.py verify --target C:\Projects\MyProject
python C:\Projects\MyProject\.maios\installer\installer.py uninstall --target C:\Projects\MyProject --receipt-out uninstall-receipt.json
```

Uninstall removes only unchanged installer-owned files and backups. A file
changed by the target project is preserved and reported, so recovery can be
partial without erasing project evolution.

## Configure the project

Open the installed project with the selected assistant and ask it to read
`START_HERE.md`. Deterministic helpers can validate and apply an accepted
configuration candidate:

```powershell
python maios.py configuration-status
python maios.py validate-configuration --candidate candidate.json
python maios.py apply-configuration --candidate candidate.json --expected-state-sha256 <current-sha256>
```

The apply command writes only project-local state, projections, backup, and
receipt. External effects remain separately unauthorized.
