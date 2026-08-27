# Architecture and ownership

## Living source and generated delivery

MAIOS Project Kernel 2.0.0 uses one implementation owner:

```text
kernel, setup, competence, adapter, runtime, installer, and template sources
-> source tests
-> declared release projection
-> generated package tree and immutable inventory
-> explicit target transition
```

`package/` is disposable generated evidence. Product behavior is never edited
there. The builder refuses missing or unsafe projection sources and binds the
source-tree, projection, source-manifest and package members.

## Deep modules and stable seams

| Seam | Hidden policy owner |
| --- | --- |
| `install.py preview/apply/verify/uninstall` | `src/maios_project_kernel/installer.py` |
| `maios.py status/compose/validate-movement` | `src/maios_project_kernel/runtime.py` |
| `maios.py operating-status/validate-resultant/apply-resultant/learning-status` | `src/maios_project_kernel/operating.py` |
| `maios.py configuration-*` | `src/maios_project_kernel/configuration.py` |
| `maios.py competence-*` | Runtime competence index and reviewed-delta policy |
| `maios-project-system` | Semantic kernel and open faculty field |
| `maios-project-competence-formation` | Portable formation and cultivation of project-local competences |
| `maios-project-host-adaptation` | Faithful translation of the neutral Kernel into host-native discovery and use |

Deterministic code validates paths, state shape, concurrency, hashes, receipts,
and recovery. The semantic host interprets the live circumstance. Candidate
projection cannot decide meaning, relevance, quality, or authority.

## Stable boot and living context

`START_HERE.md` is a stable system boot: it restores what the Kernel is, its
operating relation, and the entrances from which work can begin. It is not the
owner of the changing project situation. The current operator relation,
project sources, configuration state, recent resultants, and reachable
competences reconstruct the living context. The boot changes only when that
stable system relation changes; ordinary work evolves context and competences.

For an existing project, `maios-start-existing-project` reads the project as it
already is, forms the first useful Kernel contribution, and lets residual gaps
create the competences the work actually needs. It does not impose a fixed
pre-generated competence sequence.

## Situated composition

Two silent invariants preserve source-bound orientation and pre-projection
self-correction. Situated faculty families become candidates when the current
relation makes them material. The field remains open: an unmatched faculty can
enter with source, expected delta, invalidator, and reentry condition. No fixed
primary/support count or keyword match is behavioral proof.

## Configuration

`setup/CONFIGURATION_STATE.json` is the sole project-configuration state owner. Accepted
transitions derive:

- `.maios/context/CONTEXT_CAPSULE.json`;
- `.maios/context/SETUP_SPEC.json`;
- `project/CURRENT_STATE.md`;
- `project/PROJECT_BRIEF.md`.

The transition checks current-state identity and sequence, keeps effect
authority at `none`, stores a canonical backup, regenerates projections, and
supports recovery only while the state still matches the receipt.

## Operating relation and resultant coupling

`.maios/state/OPERATING_STATE.json` owns terminal-result history, active next
movement, causal input digests, and owner-bound learning relations.
`.maios/context/OPERATING_CONTEXT.json` is a derived projection of
configuration, host observations, competence state, faculty field, and this
operating state. It never overrides those sources.

An applied resultant readback couples inspected behavior to canonical
configuration, possibility impact, composition, evolution, projections, and
reentry under one current context hash. The transition is recoverable and
project-local. Learning becomes immediately reachable; optional classifications,
assimilation, host activation, and external effects remain separate claims.

## Reciprocal competence cultivation

Concrete work and its enabling competence advance together. Existing faculties
are reused or composed first; a real gap may form the smallest truthful local
competence relation. A causal correction is preserved at its closest owner and
can change the next matching movement. Later non-identical use supplies the
behavioral readback and may revise or invalidate it. The reviewed competence
index remains a separate deliberate owner surface, not a prerequisite for
learning. Another meta-level is added only when it changes comprehension,
execution, proof, recovery, or reentry.

## Authority and proof

The package performs project-local writes selected by explicit commands. It
does not change global configuration or grant external authority. Generated,
packaged, installed, discovered, used, verified, maintained, and human-accepted
states require different evidence. Each receipt states its claim boundary.
