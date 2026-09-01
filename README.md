# MAIOS Project Kernel

[Versione italiana](README.it.md)

Current product version: **[3.0.2](VERSION.md)**. Shared Project Kernel family:
`3.0.0`.

MAIOS Project Kernel gives a project and its AI coder a shared operating
kernel. It helps them understand the present situation, form a useful first
result, bring in the competences required by the work, learn from what happens,
and continue without reconstructing the whole conversation at every session.

The repository is the product. Its tracked [`package/`](package/) directory is
the ready-to-use self-installing projection.

Running the installer and the installed helper requires Python 3.10 or later;
no third-party Python packages are required.

A clone has two connected entrances: use the tracked package in a project, or
study and contribute to the public Kernel competence field in the repository.
The second entrance gives a coder more awareness of the system without adding
anything to an installed target.

## Start here: operator and AI coder

This README is the repository homepage for both people and AI systems. It
shows where each kind of truth lives, what the product can make possible, and
how to prepare one complete but target-owned integration without treating the
file tree as the product or turning setup into a generic interview.

An AI coder should first recover the current product relation, then choose only
the reading route that can change the present result:

| Need | Read next | What the coder should understand or return |
| --- | --- | --- |
| Establish current truth | [`AGENTS.md`](AGENTS.md), [`CURRENT_STATE.md`](CURRENT_STATE.md), [`VERSION.md`](VERSION.md), [`CHANGELOG.md`](CHANGELOG.md) | Product `3.0.2`, family `3.0.0`, current evidence, boundaries, and the selected movement |
| Understand value and possibility | [`knowledge/KERNEL.md`](knowledge/KERNEL.md), [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md), [`docs/SSK_TRANSFER_3.0.2.md`](docs/SSK_TRANSFER_3.0.2.md) | What the Kernel changes for a project, which possibilities remain open, and how the SSK relations become product-native functions |
| Integrate the package | [`package/AGENTS.md`](package/AGENTS.md), [`maios-project-integration`](package/skills/maios-project-integration/SKILL.md), [`package/INSTALL.md`](package/INSTALL.md), [`package/MANIFEST.json`](package/MANIFEST.json) | Exact target, mode, host projection, package-owned paths, preview, recovery, and unchanged surfaces |
| Configure and operate the installed Kernel | [`START_HERE.md`](package/payload/START_HERE.md), [`maios-project-system`](package/payload/skills/maios-project-system/SKILL.md), [`MAIOS_SETUP_CONTRACT.md`](package/payload/setup/MAIOS_SETUP_CONTRACT.md), [`RESULTANT_READBACK.schema.json`](package/payload/.maios/schemas/RESULTANT_READBACK.schema.json) | How context, competences, result, learning, semantic readback, and fresh reentry stay connected |
| Adapt to the active coder | [`adapters/ADAPTERS.json`](adapters/ADAPTERS.json), [`maios-project-host-adaptation`](skills/maios-project-host-adaptation/SKILL.md), [`docs/COMPATIBILITY.md`](docs/COMPATIBILITY.md) | Which native projection is available, what has only been packaged, and what still needs host observation |
| Study or contribute without installation | [`contributions/README.md`](contributions/README.md), [`maios-kernel-study`](skills/maios-kernel-study/SKILL.md), [`maios-kernel-contribution`](skills/maios-kernel-contribution/SKILL.md) | A source-bound explanation, correction, falsifier, competence, test, or contribution with no implied package or release effect |

### First readback to the operator

Before changing the target, the coder should be able to give the operator one
compact, evidence-bound readback:

- what MAIOS Project Kernel can make possible in this specific project and why;
- the exact product, family, package, and source identity it inspected;
- the target, `new_repository` or `existing_repository` mode, and active host
  inferred from real evidence;
- whether direct start is already available or which one missing relation would
  materially change integration, effect, or recovery;
- a complete functional transfer map covering Kernel, context, competences,
  state, host projection, result, learning, reentry, verification, and recovery;
- the exact files and effects proposed, what remains untouched, the recovery
  path, and every proof level that remains unobserved.

When target and effect are already clear, this readback contracts into a direct
start offer. It must not become a mandatory explanation phase, repeat known
context, or ask the operator to design the solution before the Kernel has shown
what is useful and possible.

### Capability and value map

The following map is the quickest way for an AI to understand the whole
product without eagerly loading every competence:

| Product relation | Value in the project | Decisive owner sources |
| --- | --- | --- |
| Adaptive direct or expanded entry | Begins immediately in a legible project and expands shared understanding only when it changes the movement | [`AUTONOMOUS_ENTRY_CONTRACT.json`](kernel/AUTONOMOUS_ENTRY_CONTRACT.json), [`maios-project-integration`](skills/maios-project-integration/SKILL.md) |
| Shared, correctable context | Connects operator intent, actual sources, facts, assumptions, unknowns, and authority without storing the transcript as truth | [`MAIOS_SETUP_CONTRACT.md`](setup/MAIOS_SETUP_CONTRACT.md), [`maios-project-context`](package/payload/skills/maios-project-context/SKILL.md) |
| Open possibility and situated direction | Keeps unrepresented possibilities reachable, gives reasons for useful alternatives, and forms one revisable movement | [`SYSTEM_KERNEL.md`](kernel/SYSTEM_KERNEL.md), [`FACULTY_FIELD.json`](kernel/FACULTY_FIELD.json) |
| Pertinent competence composition | Lets the work select or form the smallest capability that can change the result, without a fixed palette becoming the system limit | [`COMPETENCE_CULTIVATION_PROTOCOL.md`](kernel/COMPETENCE_CULTIVATION_PROTOCOL.md), [`maios-project-competence-formation`](package/payload/skills/maios-project-competence-formation/SKILL.md) |
| Useful resultant and semantic readback | Makes the actual result, meaning changes, consequences, and no-change relations shape what happens next | [`RESULTANT_READBACK.schema.json`](schemas/RESULTANT_READBACK.schema.json), [`src/maios_project_kernel/operating.py`](src/maios_project_kernel/operating.py) |
| Plural owner-native learning | Returns each reusable correction to the closest competence it must change, then tests it in later non-identical work | [`EVOLUTION_CONTRACT.json`](kernel/EVOLUTION_CONTRACT.json), [`COMPETENCE_CULTIVATION_PROTOCOL.md`](kernel/COMPETENCE_CULTIVATION_PROTOCOL.md) |
| Compact causal continuity | Preserves the live causal margin, genuinely open fronts, one present focus, and a fresh-session reentry without replaying the conversation | [`OPERATING_STATE.template.json`](state/OPERATING_STATE.template.json), [`START_HERE.md`](templates/project/START_HERE.md) |
| Host-native adaptation | Projects the same Kernel into the selected coder's native discovery path while keeping host presence distinct from observed use | [`ADAPTERS.json`](adapters/ADAPTERS.json), [`maios-project-host-adaptation`](skills/maios-project-host-adaptation/SKILL.md) |
| Deterministic integration and recovery | Previews exact package-owned changes, refuses conflicts, applies an immutable plan, verifies identity, and preserves project-owned evolution on uninstall | [`INSTALLATION.md`](docs/INSTALLATION.md), [`installer.py`](src/maios_project_kernel/installer.py) |

These relations are one Kernel in motion. The table is an orientation map, not
a closed feature catalogue: a present source, competence, host, or schema must
not become the limit of what later project work can make reachable.

### Prepare the complete integration movement

Before acting, the coder should internally connect the whole delivery relation:

```text
repository identity and target evidence
-> complete functional map and material unknowns
-> direct start or one result-changing clarification
-> exact preview of paths, effects, unchanged surfaces, and recovery
-> target-owned apply
-> native discovery of START_HERE and the pertinent competences
-> first useful correctable result
-> owner-native learning and compact reentry
-> evidence-bound report of what is represented, installed, discovered,
   exercised, changed, and still unobserved.
```

This preparation keeps all product functions reachable, but it does not force
all skills into context or all future decisions into the first plan. The real
project and the operator remain the owners of situated configuration and later
evolution.

### First available action

Clone the repository, open its root with your coder, and say:

```text
Read AGENTS.md and the maios-project-integration competence. Use this README as
the repository map. Tell me what this Kernel can make possible here and the
complete target-owned integration movement. If target and effect are already
clear, offer the direct start; otherwise explain only the missing relation that
would materially change integration, effect, or recovery.
```

Nothing installs merely because the repository was opened. After the exact
preview is accepted, the available command path is:

```powershell
Set-Location .\package
python install.py preview --target C:\Projects\MyProject --mode new_repository --host codex --plan-out install-plan.json
python install.py apply --plan install-plan.json
```

For a project that already exists, use `--mode existing_repository`. Replace
`codex` with the selected host id described below.

## Study and contribute

Open the repository root with a capable coder and say:

```text
Read AGENTS.md and the maios-kernel-study competence. Reconstruct the Kernel
from its public sources, explain the relation you see, and show which source,
evidence, inference, and open question support your explanation.
```

The public source field connects:

| Surface | Function |
| --- | --- |
| [`knowledge/KERNEL.md`](knowledge/KERNEL.md) | Public source for the Kernel's constitutive relation, KA, FDLA, Meta_Skill, competence, context, and learning |
| [`maios-kernel-study`](skills/maios-kernel-study/SKILL.md) | Studies, explains, compares, and questions the Kernel from public sources |
| [`maios-kernel-contribution`](skills/maios-kernel-contribution/SKILL.md) | Turns a human or AI idea, method, correction, or falsifier into a source-bound contribution |
| [`contributions/GPT_PRO_START.md`](contributions/GPT_PRO_START.md) | Opens one bounded GPT Pro contribution cycle |

These competences act on the repository and are not part of the current
installable projection. A human, GPT Pro, Codex, or another capable model can
contribute through the same canonical relation. Contribution, merge, package
projection, release, installation, and observed use remain distinct effects.

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
autonomous living repository sources
plus reviewed RepoKernel functions translated into owner-native relations
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
| `knowledge/`, `contributions/` | Repository-native Kernel understanding and competence contribution field |
| `setup/`, `project/`, `state/` | Canonical configuration and compact project continuities |
| `src/maios_project_kernel/` | Deterministic projection, installer, configuration, runtime, host state, and operating readback |
| `adapters/` | Project-local host projections |
| `templates/` | Distribution and installed-project entry surfaces |
| `release/repokernel/` | Source-bound RepoKernel input, generated functional map, and translation receipt |
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

The self-configuring package contains owner-native translations of reviewed
neutral RepoKernel functions,
but does not import MAIOS Form answers, private RepoKernel source, private
D-ND/TMx topology, credentials, runtime state, or lifecycle hooks. The
separately Form-generated Project Kernel is another delivery pipeline with its
own context, bytes, and proof.

See [Architecture](docs/ARCHITECTURE.md),
[Provenance](docs/PROVENANCE.md), and [Receipts](docs/RECEIPTS.md) for depth.

## License

Source and generated package content, excluding names and trademarks, are
available under the [MIT License](LICENSE). See
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and
[TRADEMARKS.md](TRADEMARKS.md).
