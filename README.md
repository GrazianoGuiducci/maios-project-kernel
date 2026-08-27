# MAIOS Project Kernel

[Versione italiana](README.it.md)

MAIOS Project Kernel gives a project and its AI coder a shared operating
kernel. It helps them understand the present situation, form a useful first
result, bring in the competences required by the work, learn from what happens,
and continue without reconstructing the whole conversation at every session.

The repository is the product. Its tracked [`package/`](package/) directory is
the ready-to-use self-installing projection.

## Start here

Clone or download the repository, open `package/` with your coder, and say:

```text
Read AGENTS.md and the maios-project-integration competence. Explain what this
package can add to my project and how you would integrate it. After we agree,
prepare the installation plan.
```

The coder first forms a correctable shared understanding. It then previews an
exact project-local transition. Nothing installs merely because the repository
was opened.

```powershell
Set-Location .\package
python install.py preview --target C:\Projects\MyProject --mode new_repository --host codex --plan-out install-plan.json
python install.py apply --plan install-plan.json
```

For a project that already exists, use `--mode existing_repository`. Replace
`codex` with the selected host id described below.

## What happens after installation

```text
operator and real project
-> stable Kernel boot
-> new-project or existing-project activation
-> living context and possibility horizon
-> pertinent competences act alone or together
-> first useful correctable result
-> reusable learning returns to the closest competence
-> the next session begins from the changed project field.
```

The Kernel is not a predefined answer, a fixed workflow, or a catalogue of
skills. It is the project-level system that keeps intent, sources, context,
possibilities, competences, results, learning, and reentry connected while the
project changes.

## Two starting conditions

### New project

The Kernel establishes only the initial identity and context needed to move:

- what the person is trying to change;
- the sources, people, boundaries, and unknowns already present;
- a small set of meaningfully different possibilities with reasons;
- one correctable direction;
- the first useful result and a way to test it.

It returns value before asking for non-decisive detail.

### Existing project

The Kernel enters as a new participant rather than replacing the project's
identity. It reads the existing sources, instructions, conventions, current
state, active work, and operator signal. It then:

- preserves existing material;
- reconstructs the live context without repeating what the project knows;
- exposes the first useful Kernel contribution;
- composes the competences already reachable;
- forms only the additional competences that real work proves necessary.

The installer never performs a hidden semantic merge. Divergent target paths
remain conflicts for the coder and operator to resolve explicitly.

## Stable boot, living context

Installed projects start from `START_HERE.md`. This is a stable system boot,
not a continually rewritten project diary. It restores:

- what the Kernel is;
- how the project enters it;
- how startup, context, host adaptation, competence work, learning, and reentry
  relate.

The changing context remains in the current operator relation, actual project
sources, `setup/CONFIGURATION_STATE.json`, `project/CURRENT_STATE.md`, recent
resultants, and the competences that act. The boot changes only when the stable
Kernel relation changes.

## Included operating competences

| Competence | Function |
| --- | --- |
| `maios-project-integration` | Understands and explains the repository package, then prepares its target-owned integration |
| `maios-project-system` | Keeps the complete project-level Kernel relation reachable |
| `maios-start-new-project` | Forms the first situated movement for a genuinely new project |
| `maios-start-existing-project` | Activates the Kernel inside an operating project without replacing its identity |
| `maios-project-context` | Reconstructs living context, useful possibilities, direction, proof, and competence handoffs |
| `maios-project-competence-formation` | Forms or evolves the smallest useful project-local competence when a real gap remains |
| `maios-project-host-adaptation` | Translates the neutral Kernel relation into the current coder's native conventions |

Competences are the operating knowledge of the system. They do the work for
which they are pertinent, retain reusable causal learning, and can improve,
compose, be superseded, or retire through later use.

## How the system evolves

The installed Kernel is a seed. Ordinary evolution does not depend on a
standing software-upgrade mechanism:

```text
real work
-> pertinent competence acts
-> actual result and correction
-> reusable difference changes the closest owner
-> later non-identical work uses, revises, or invalidates that learning.
```

When existing competences cannot carry a material relation, the competence-
formation faculty creates the smallest useful owner-native body: a method,
reference, protocol, function, skill, or coordinating relation. It does not
copy the private whole-kernel generator into the project.

If a future structural update becomes necessary, it can be delivered as a
competence able to understand and update its own system. That is not required
for the current product.

## Supported coding hosts

Every host receives the same neutral Kernel and competence sources. The
profile only supplies a native starting projection; the host-adaptation
competence translates any remaining mechanics without creating a different
Kernel.

| Host id | Coder or harness | Initial project-local projection |
| --- | --- | --- |
| `codex` | ChatGPT / Codex coding agent | `.agents/skills/` with all portable owners |
| `claude` | Claude Code | `.claude/skills/` with system and host adaptation |
| `opencode` | OpenCode | `.opencode/skills/` with system and host adaptation |
| `hermes` | Hermes | `.hermes/skills/` with system and host adaptation |
| `openclaw` | OpenClaw | `.agents/skills/` with system and host adaptation |
| `pi` | Pi coding agent | `.agents/skills/` with system and host adaptation |
| `dsh` | DeepSeek Harness | `.agents/skills/` with system and host adaptation |
| `generic` | Another capable coder | root instructions and neutral `skills/` sources |

Installation, native discovery, state reading, semantic use, observed result,
and maintained reentry remain distinct states. A projected path does not claim
that a particular host has already exercised the Kernel.

See [host compatibility](docs/COMPATIBILITY.md) for host-specific notes.

## Installation contract

The generated `package/` tree contains its own exact manifest and SHA-256
inventory. Installation uses an immutable preview plan:

- `new_repository` accepts only an absent or empty target and promotes a
  complete adjacent staging directory atomically;
- `existing_repository` inventories the target, creates missing paths,
  preserves identical paths, and refuses divergent content;
- a changed package or target invalidates the plan;
- interrupted existing-project installation can recover from its local
  `PENDING` journal;
- reapplying the same package to an unchanged installation is idempotent;
- uninstall removes only unchanged installer-owned files;
- files evolved by the project are preserved and reported.

The installer does not modify global host configuration, hooks, plugins,
providers, credentials, services, repositories, or other projects.

Verification and recovery commands:

```powershell
python C:\Projects\MyProject\.maios\installer\installer.py verify --target C:\Projects\MyProject
python C:\Projects\MyProject\.maios\installer\installer.py uninstall --target C:\Projects\MyProject --receipt-out uninstall-receipt.json
python install.py recover-pending --target C:\Projects\MyProject
```

The complete procedure is in [Installation](docs/INSTALLATION.md).

## Project-local operation

After installation, open the target project and ask the coder to read
`START_HERE.md`. Useful local commands include:

```powershell
python maios.py status
python maios.py configuration-status
python maios.py competence-status
python maios.py learning-status
python maios.py operating-status
```

Configuration helpers can validate and apply an accepted candidate with
concurrency protection and recovery. Composition and resultant helpers expose
the represented field and update continuity when that durable movement is
actually needed; they do not replace semantic judgment by the coder and
operator.

## Package and source structure

```text
living repository sources
-> declared release/PROJECTION.json
-> deterministic tracked package/ projection
-> exact MANIFEST.json and PACKAGE_INVENTORY.json
-> target-owned preview and installation
-> project-local Kernel, state, competences, learning, and reentry.
```

| Owner | Purpose |
| --- | --- |
| `kernel/` | Semantic Kernel, open faculty field, composition, and competence cultivation |
| `skills/` | Integration, system, startup, context, competence formation, host adaptation, and repository-source competences |
| `setup/`, `project/`, `state/` | Canonical configuration and compact project continuities |
| `src/maios_project_kernel/` | Deterministic projection, installer, configuration, runtime, host state, and operating readback |
| `adapters/` | Project-local host projections |
| `templates/` | Distribution and installed-project entry surfaces |
| `release/PROJECTION.json` | Complete source-to-package mapping |
| `package/` | Generated, tracked, directly usable installation surface |
| `tests/` | Source, package, installation, recovery, state, and behavior fixtures |

`package/` is generated from the living owners and must not be edited by hand.

## Build from source

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B tools\build_release.py
python -B tools\verify_distribution.py
```

The builder regenerates `package/`, its manifest, and its exact inventory.

## Current evidence and limits

The source, deterministic package projection, inventory, installer mechanics,
startup routing, host projections, and project-local state contracts are
inspectable in this repository. These do not by themselves prove semantic
acceptance by a real operator, native use by every host, or maintained behavior
across later non-identical work. Those observations remain separate evidence.

The self-configuring package does not import MAIOS Form answers, private
RepoKernel source, private D-ND/TMx topology, credentials, runtime state, or
lifecycle hooks. The separately Form-generated Project Kernel is another
delivery pipeline with its own builder, context, bytes, and proof.

See [Architecture](docs/ARCHITECTURE.md),
[Provenance](docs/PROVENANCE.md), and [Receipts](docs/RECEIPTS.md) for depth.

## License

Source and generated package content, excluding names and trademarks, are
available under the [MIT License](LICENSE). See
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and
[TRADEMARKS.md](TRADEMARKS.md).
