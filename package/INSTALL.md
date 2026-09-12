# Install MAIOS Project Kernel 4.1.2 — repository package

The ready-to-install distribution is in `package/`. Run `install.py` from this
directory. `preview` creates a plan for a target folder and coding host;
`apply` installs that plan. Opening or downloading the package does not execute it.

## Requirement

The installer and the installed `maios.py` helper require Python 3.10 or later.
They use only the Python standard library.

Keep plans and CLI output receipts outside this package, the source repository
and the target. The examples use the system temporary directory. The CLI checks
this before any output or removal effect; the package inventory stays immutable.

## Install in the selected folder

From `package/`, set the target to the folder where the kernel will be used.
The target may be empty, contain an existing project, or contain this source
clone. Use the current coder's host id: `opencode`, `codex`, `claude`, `hermes`,
`openclaw`, `pi`, `dsh`, or `generic` (see `adapters/ADAPTERS.json`).

```powershell
$maiosTarget = "C:\Projects\MyProject"
$maiosHost = "opencode"
$maiosPlan = Join-Path $env:TEMP "maios-install-plan.json"
python install.py preview --target $maiosTarget --host $maiosHost --plan-out $maiosPlan
python install.py apply --plan $maiosPlan
```

The preview reports the selected folder, host, changes and any conflicts.
`apply` uses that exact plan. After installation, read `START_HERE.md` **in the
target folder** and continue through `skills/maios-project-system/SKILL.md`.
That is the operating entry for understanding and using the kernel in context.

## Automatic folder handling

The default `--mode auto` selects `new_repository` for an absent or empty
folder and `existing_repository` for a non-empty folder. These are filesystem
modes, not questions about the user's project. Reapplying the same package and
host preserves the original installation mode. An explicit `--mode` remains
available when a particular filesystem behavior is needed.

`new_repository` builds the complete target in an adjacent attempt-owned
directory and atomically moves it into place. Reapplying the same artifact to
its unchanged installed target is idempotent.

`existing_repository` inventories the existing project, classifies every destination as
create, preserve-identical, or conflict, and refuses divergent content. It
backs up pre-existing identical target paths and never performs a semantic
merge or hidden overwrite. A changed target invalidates the plan. Before its
first write, apply stores a project-local `PENDING` journal. If the process or
machine stops, run `python install.py recover-pending --target <target>` from
this package directory; recovery removes only unchanged attempt-owned
bytes and preserves evolved or uncertain files. A planned path alone does not
establish ownership; if CURRENT has committed the same plan, recovery only
finishes journal cleanup.

Uninstall requires the valid current installation receipt, including when an
explicit receipt copy is supplied. A different, invalid or missing CURRENT
refuses deletion. Archived receipts can still support read-only `verify`, which
reports their current relation separately from historical consistency. Empty
directories in existing projects remain because their ownership is unrecorded.
Unregistered bytecode also remains and is reported; a matching name does not
establish ownership. Normal MAIOS launchers suppress automatic bytecode creation.

A conflict is returned to `maios-project-integration` as a target-owner
relation. The coder can then propose the smallest explicit merge or placement
movement without weakening the installer's non-overwrite contract.

## Reinstallation and version migration

Reapplying this exact artifact to its unchanged installation is idempotent.
That property is not a cross-version upgrade claim. This package does not
implement an in-place migration from a project installed by another product
version. Preserve the existing
target and its project-evolved files; if migration becomes necessary, treat it
as a separate target-owned movement with an explicit inventory, reconciliation,
effect, and recovery relation.

## Verify and recover

```powershell
python C:\Projects\MyProject\.maios\installer\installer.py verify --target C:\Projects\MyProject
$maiosReceipt = Join-Path $env:TEMP "maios-uninstall-receipt.json"
python C:\Projects\MyProject\.maios\installer\installer.py uninstall --target C:\Projects\MyProject --receipt-out $maiosReceipt
```

Recovery removes only installer-created files whose bytes are still identical.
Files evolved by the project remain in place and are listed in the receipt.
The installer never changes global host configuration, hooks, plugins,
credentials, services, repositories, or another project.

The first installation carrying the new update standard records its exact
baseline in `.maios/receipts/install/CURRENT.json`. Future selected updates use
`.maios/kernel/UPDATE_CONTINUITY.md` to compare original distribution, local
learning and proposed source, preserve state compatibility and recover the
affected files. The standard starts here; no earlier-installation migration
adapter is required.
