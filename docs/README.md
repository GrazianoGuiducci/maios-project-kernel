# Documentation map

[Product overview](../README.md) · [Presentazione italiana](../README.it.md)

## Use the package

- [Usage](USAGE.md) / [Guida d'uso](USAGE.it.md): integration, project startup,
  competences, learning, reentry and local status commands.
- [Installation](INSTALLATION.md): exact preview/apply, conflicts, verification,
  recovery and uninstall.
- [Compatibility](COMPATIBILITY.md): supplied host projections and what remains
  to be observed in each host.
- [Update continuity](../kernel/UPDATE_CONTINUITY.md): baseline, local knowledge
  and a proposed new version.
- [Instance coordination](INSTANCE_COORDINATION.md): shared work and continuation
  across agents and harnesses.

## Understand or contribute

- [Kernel knowledge](../knowledge/KERNEL.md): meaning, operating relations and
  the sources through which competences act.
- [Architecture](ARCHITECTURE.md): source owners, generated distribution and
  installed state.
- [Contributing](../CONTRIBUTING.md) and [competence contributions](../contributions/README.md).
- [Build](GENERATED_KERNEL_BUILD.md): reproduce the included distribution from
  public source and its retained selection; no private compiler access is needed.
- [Provenance](PROVENANCE.md): content identity, retained inputs and evidence limits.

## Current product and history

[VERSION.md](../VERSION.md) identifies product and family versions.
[CURRENT_STATE.md](../CURRENT_STATE.md) identifies current source work.
[CHANGELOG.md](../CHANGELOG.md) and numbered release notes preserve version history;
their old claims describe their stated versions, not the current product.
[4.1.0 notes](RELEASE_4.1.0.md) and [evidence](RELEASE_4.1.0_EVIDENCE.md) are the
current numbered release's explanation and dated observations.

Historical transfer and review files remain available for a source comparison.
They are not required reading for installation or ordinary use.

## Maintainer production

[Selection renewal](RENEW_KERNEL_SELECTION.md) requires access to a private
production compiler. The public repository includes the exported inputs, plan
and product-side consumer. Schema identifiers, compiler identities and historical
receipts retain their literal provenance; they are technical records, not user
requirements or additional products to acquire.

`templates/` owns generated entry text; `skills/` and `kernel/` own native
methods; `release/PROJECTION.json` maps the source distribution and the retained
selection supplies selected bodies. Never edit `package/` by hand.

## Source ownership map

| Source | What belongs here |
| --- | --- |
| `kernel/`, `skills/` | Operating relations, knowledge and competence methods |
| `knowledge/`, `contributions/` | Public study and contribution, outside the installed projection |
| `setup/`, `project/`, `state/` | Configuration contracts and project state templates |
| `src/maios_project_kernel/` | Builder, installer, local state services and recovery |
| `adapters/`, `templates/` | Host projections and generated entry text |
| `release/` | Projection mapping, retained generation inputs and selection |
| `package/` | Generated installation distribution |
| `tests/` | Source, distribution and project-state checks |

[Receipts](RECEIPTS.md) explains the records produced by local operations.
