# MAIOS Project Kernel

[Italian version](README.it.md)

MAIOS Project Kernel is a portable, self-installing project system for people
working with AI assistants. It starts from the person's real situation and
sources, forms an early correctable result, composes only the faculties that
change the present movement, and preserves causal learning and reentry in the
project itself.

The public `v2.0.0` Release is available from the canonical GitHub repository.
This source contains the forward-resultant completion of the same 2.0.0 line.
Until publication is reconciled, the public Release and this living source
remain distinct identities.

- [Download Release 2.0.0](https://github.com/GrazianoGuiducci/maios-project-kernel/releases/tag/v2.0.0)
- [Inspect or star the repository](https://github.com/GrazianoGuiducci/maios-project-kernel)

Source publication and a Release do not claim host activation, semantic
results, maintained reentry, or public runtime operation.

This release is a foundation, not a ceiling: new competences, hosts and forms
of embodiment can enter when a future circumstance makes their relations
useful, without turning the current architecture into a fixed ontology.

## What changed in 2.0.0

The repository is the living source system. `package/` and the ZIP are generated
projections, never a second hand-authored implementation:

```text
living source, tests, and accepted contracts
-> deterministic package projection and inventory
-> self-installing archive
-> explicit target plan and receipt
-> installed project
-> separate host discovery, use, result, and maintained-reentry evidence
```

The system includes:

- a source-bound, open-horizon semantic kernel;
- an open causal faculty field with circumstance-sensitive composition;
- MAIOS situated configuration with one canonical state, a hash-linked Context
  Capsule and SetupSpec, compact human projections, concurrency checks, and
  recovery;
- an autological operating context that exposes current capability relations,
  causal invalidations, uncertainty, and authority without claiming semantic
  correctness or activation;
- forward-resultant readback that couples actual results, possibility impact,
  next movement, and owner-bound causal learning to configuration and reentry;
- reciprocal competence cultivation: concrete work tests and improves the
  competence that enables it; causal readback changes the closest owning
  relation, matching later movements exercise it, and non-identical use can
  revise or strengthen it;
- deterministic `preview`, `apply`, `verify`, and `uninstall` installation for
  empty or existing repositories without hidden overwrite;
- project-local adapters for Codex, Claude Code, OpenCode, DSH, Hermes, and a
  generic host path;
- explicit separation of packaged, installed, discovered, used, verified, and
  maintained states.

## Build from source

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B -m unittest discover -s tests -v
python -B tools\build_release.py
python -B tools\verify_distribution.py
```

The builder reads [`release/PROJECTION.json`](release/PROJECTION.json), projects
only declared canonical sources, writes `package/MANIFEST.json` and an exact
SHA-256 inventory, then creates `dist/maios-project-kernel-setup-v2.0.0.zip`.

## Install the generated archive

Extract the archive into a temporary distribution folder. Installation does
not run automatically.

```powershell
python install.py preview --target C:\Projects\MyProject --mode new_repository --host codex --plan-out install-plan.json
python install.py apply --plan install-plan.json
```

For an existing repository use `--mode existing_repository`. The plan classifies
every destination as new, identical, or conflicting; divergent content blocks
the transition. See [installation](docs/INSTALLATION.md) and [host
compatibility](docs/COMPATIBILITY.md).

After installation, open the target project and ask the assistant to read
`START_HERE.md`. Installation proves bytes and receipts only. A fresh host must
still demonstrate native discovery, state use, relevant faculty behavior, an
observable result, and later reentry.

## MAIOS Setup and the Form route

This repository owns the manual `self_configuring` entry. It begins neutral and
forms its situated configuration after acquisition. It does not import MAIOS
Form state, P1-P5 answers, private workspace topology, credentials, lifecycle
hooks, or inherited effect authority. The Form-generated route is a later,
independent comparison after the manual 2.0.0 vertical is complete.

## Source layout

| Owner | Purpose |
| --- | --- |
| `kernel/` | Semantic kernel, faculty composition, evolution, and competence cultivation |
| `setup/` | MAIOS configuration contract and canonical-state template |
| `src/maios_project_kernel/` | Installer, configuration, operating relation, runtime, and builder |
| `competences/`, `state/`, `schemas/` | Project-local competence index, forward-resultant learning state, and event contracts |
| `adapters/` | Host discovery projections |
| `templates/` | Distribution and installed-project entry files |
| `release/PROJECTION.json` | Complete source-to-package mapping |
| `tests/` | Source, package, installation, state, recovery, and behavior fixtures |

Architecture and evidence boundaries are documented in
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and
[docs/PROVENANCE.md](docs/PROVENANCE.md).

## License

Source and generated package content, excluding names and trademarks, are
available under the [MIT License](LICENSE). See
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and
[TRADEMARKS.md](TRADEMARKS.md).
