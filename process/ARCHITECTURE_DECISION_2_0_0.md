# Architecture decision: MAIOS Project Kernel 2.0.0

## Behavioral owner

The package must help an AI host and a person form one situated project system:
recover the present relation, illuminate what matters, compose the faculties
that change the movement, produce a useful result, inspect it, learn only the
reviewed delta, and reenter without replaying the conversation.

## Design A: single narrative kernel

One large system document and one thin skill would contain orientation,
configuration, routing, learning, and boundaries.

It has a small visible surface, but callers must interpret a monolith; state,
composition, installer, proof, and recovery are not independently testable.
Replacing many files with this document would lose executable installation,
typed continuity, host evidence, and falsifiable behavior.

## Design B: deep orchestration kernel

The public seam is small:

```text
install.py preview | apply | verify | uninstall
maios.py status | compose | validate-movement | operating-status
maios.py validate-resultant | admit-resultant
one maios-project-system skill
```

Behind it the package owns:

- deterministic artifact, target, conflict, receipt, and recovery policy;
- one canonical setup state and one concise human reentry projection;
- an open faculty field of causal functions, not a closed skill catalogue;
- a composition protocol that keeps permanent invariants silent, proposes
  known material relations, admits emergent faculties, and records why each
  selected faculty changes the movement;
- host-native discovery projections selected by the installer;
- separate evidence for installed, discovered, used, and maintained states.

## Decision

Select Design B. It hides substantial policy behind two narrow interfaces and
lets the semantic host remain free where deterministic code cannot decide
meaning. Design A survives only as the concise `SYSTEM_KERNEL.md` source read by
the skill; it is not the whole product.

The interface is value/result-oriented: preview returns an immutable plan;
apply accepts that exact plan; composition returns candidates and unmatched
relations rather than executing a keyword router. Effects and failures remain
visible in receipts.

## Source-to-artifact ownership

The selected design is implemented in the living repository before packaging:

```text
kernel/ + setup/ + competences/ + adapters/ + src/ + templates/
-> source tests and behavioral fixtures
-> release/PROJECTION.json
-> generated package/
-> deterministic ZIP
```

`package/` is never a second implementation surface. If useful logic first
appears in a payload draft, it must be recovered into its canonical source owner
before the generated tree replaces the draft. Source-to-package identity is
part of the build receipt.

Configuration and competence cultivation are deep modules behind `maios.py`.
Configuration owns one structured state and regenerates Context Capsule,
SetupSpec, current-state and brief projections with concurrency and recovery.
Competence cultivation advances concrete work and its enabling competence
reciprocally, admits only independently reviewed local deltas, and stops when
another meta-level changes no material relation.

## Operating relation decision

Two implementation forms were compared for the missing terminal coupling:

- a stateful `OperatingKernel` object coordinating every subsystem and holding
  semantic selection;
- a value/result module deriving an operating context from explicit state and
  admitting only a reviewed terminal readback.

Select the value/result module. The first form would centralize meaning and
make the current class design the ceiling of future composition. The selected
`operating.py` owns deterministic causal bookkeeping, freshness invalidation,
resultant validation, state concurrency, terminal projections, recovery, and
receipts. The semantic host and independent reviewer retain interpretation and
approval. The module can evolve behind the stable commands without becoming a
manager object, automatic self-improvement loop, or effect authority.

## Deletion and replacement test

The old package can be removed without changing callers that use `install.py`,
`maios.py`, or `maios-project-system`. Host adapter paths and internal faculty
families may evolve behind those seams. The 2.0.0 source retains no dependency
on old lifecycle hooks, duplicated skill owners, or the historical Form state.

## Proof

- new empty target installation;
- same-plan and same-artifact idempotency;
- changed target or divergent file refusal;
- existing-repository preview with explicit conflict classification;
- recovery that removes only unchanged installer-owned bytes;
- native skill discovery from the selected host projection;
- a situated composition fixture whose context change reroutes faculties;
- a later reentry that uses reviewed state without transcript dependence.
