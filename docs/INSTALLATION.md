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
product version. Preserve the
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

The first installation carrying the new update standard records its exact
baseline in `.maios/receipts/install/CURRENT.json`. Future selected updates use
`.maios/kernel/UPDATE_CONTINUITY.md` to compare original distribution, local
learning and proposed source, preserve state compatibility and recover the
affected files. The standard starts here; no earlier-installation migration
adapter is required.

Installer verification also checks that this baseline matches the saved
original plan and package identity. A changed local knowledge body remains
`target_evolved`; it does not invalidate a coherent historical baseline.
Receipt ownership and backup maps must also match the original plan. An invalid
current receipt blocks reapplication and uninstall without changing files or
removing the receipt. `verify` refuses to infer installation success from a
corrupt map. General `python maios.py status` uses the same canonical state
readers as the configuration and operating commands.

An operational configured intent requires a non-empty `intent_source` in the
configuration candidate. Attribute expressed, inferred or retained intent in
the form appropriate to its actual sources; no closed vocabulary or additional
operator interview is required. Unresolved setup can remain provisional.

The system competence uses `python maios.py source-contact-status` and
`python maios.py record-source-contact --observation contact.json --expected-state-sha256 <current-sha256>`
to continue an actual source observation. The observation records `observed_at`
with timezone, `status` (`observed` or `unavailable`), `source_identity` (exact
revision for success, null for failure), and `summary`, including no-change
results. State lives under `source_contact` in the canonical configuration.
These local commands perform no network or background work.
