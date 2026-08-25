# Install MAIOS Project Kernel 2.0.0 — generated distribution

The archive is self-installing, not self-executing. Extract it to a temporary
directory, select an exact target and host, preview the transition, then apply
that exact plan.

## New project

```powershell
python install.py preview --target C:\Projects\MyProject --mode new_repository --host codex --plan-out install-plan.json
python install.py apply --plan install-plan.json
```

`new_repository` accepts only an absent or empty target. The first apply builds
the complete target in an adjacent attempt-owned directory and atomically moves
it into place. Reapplying the same artifact to its unchanged installed target
is idempotent.

## Existing project

```powershell
python install.py preview --target C:\Projects\Existing --mode existing_repository --host codex --plan-out install-plan.json
python install.py apply --plan install-plan.json
```

This mode inventories the existing project, classifies every destination as
create, preserve-identical, or conflict, and refuses divergent content. It
backs up pre-existing identical target paths and never performs a semantic
merge or hidden overwrite. A changed target invalidates the plan. Before its
first write, apply stores a project-local `PENDING` journal. If the process or
machine stops, run `python install.py recover-pending --target <target>` from
this extracted distribution; recovery removes only unchanged attempt-owned
bytes and preserves any evolved file.

## Verify and recover

```powershell
python C:\Projects\MyProject\.maios\installer\installer.py verify --target C:\Projects\MyProject
python C:\Projects\MyProject\.maios\installer\installer.py uninstall --target C:\Projects\MyProject --receipt-out uninstall-receipt.json
```

Recovery removes only installer-created files whose bytes are still identical.
Files evolved by the project remain in place and are listed in the receipt.
The installer never changes global host configuration, hooks, plugins,
credentials, services, repositories, or another project.
