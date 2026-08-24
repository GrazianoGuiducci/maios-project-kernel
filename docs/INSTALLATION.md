# Installation

## Supported path: new project

1. Download the latest release archive.
2. Verify its SHA-256 against the checksum shown in the release notes.
3. Create a new, empty folder.
4. Extract the archive contents directly into that folder.
5. Open the folder with the selected assistant.
6. Ask the assistant to read `START_HERE.md` and begin configuration.

On PowerShell, a downloaded archive can be checked with:

```powershell
Get-FileHash -Algorithm SHA256 .\maios-project-kernel-setup-v1.6.0.zip
```

## Cloning this repository

Clone the repository when you want to inspect or contribute to the public
distribution. The installable payload lives under `package/`; cloning is not
the recommended way to start an end-user project because the clone retains the
distribution repository's Git history and remote.

## Existing repositories

Do not copy this release over an existing repository. Existing projects can
already have instructions, skills, state, authority boundaries, or names that
collide with the package. A future merge mode must inspect those conditions and
produce a reviewable plan before mutation.

## Optional Codex lifecycle projection

The Project Kernel works without hooks. Version `1.6.0` also packages the
optional Codex projection introduced in `1.4.0`. From the accepted project
root, inspect it before any write:

```powershell
python .repokernel/lifecycle/install.py --project-root . --check
```

Install it only after the project owner selects that effect:

```powershell
python .repokernel/lifecycle/install.py --project-root . --install
```

The installer refuses non-identical conflicts, records what it creates, and
supports bounded removal:

```powershell
python .repokernel/lifecycle/install.py --project-root . --uninstall
```

An installation receipt proves installation only. A fresh Codex session and a
real mutation/readback cycle are still required before claiming activation.
