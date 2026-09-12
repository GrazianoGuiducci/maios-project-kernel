# MAIOS situated configuration contract — canonical source

Configuration makes the package specific to the present person, project,
domain, sources, and host without deciding a solution form in advance.

Context continues to be built from sources, work and consequences after setup.
The assistant derives a correctable intent and lets competences produce useful
solutions. Preserve whether it was expressed or inferred, its reasons and what
could change that reading in `operator_relation.intent_source` and the relevant
source-bound knowledge. An inferred intent does not become an operator quote
or effect authority when saved.

## Entry modes

For a new project, `maios-start-new-project` establishes the first project
identity, direction and useful result with the operator. For an existing
project or system, `maios-start-existing-project` first preserves its identity,
sources, conventions and live movement, then finds the smallest useful Kernel
contribution. Both continue through `maios-project-context`.

`START_HERE.md` orients the coder at startup and reentry. `AGENTS.md` connects the
host to the system competence, which owns the operating entry. The operator,
project sources, canonical configuration and pertinent competences reconstruct
the living context; durable state changes when the resulting causal difference
changes later behavior or reentry.

This repository package is the `self_configuring` entry. It does not import Form state,
P1-P5 answers, a Terminal Context Field, or an accepted external case. A Form
route may later converge on the same situated-project function, but remains a
different temporal source and builder until independently compared.

The self-configuring entry acquires context from the present request, project
and host. The Form-generated entry starts from context already accepted in the
Form. Both can refine that understanding through later work.

## Result

The first useful configuration preserves:

- the person's current intent and point of view;
- the real work, problem, or desired change;
- facts, hypotheses, contradictions, unknowns, and source references;
- possibilities with their reasons and what could change them;
- the selected or still-open direction and its review state;
- the result to produce; beneficiary, value mechanism, deliverable and an
  experiment when those relations help the particular project;
- people, responsibilities, environment, and observed host capabilities;
- the project-local data boundary, private fields, any explicitly allowed
  external projection, and provider consent kept separate from project intent;
- the selected faculty composition and why every faculty changes the movement;
- exact effect authority, which remains `none` until an effect actually exists.

## Completion

Configuration becomes `configured` when the project has a concrete case,
first useful result, attributable sources, selected
movement, and recoverable reentry. It does not require every unknown to close.
An experiment or a reviewer is not a condition for a project to be configured.
When a hypothesis calls for a proof plan, preserve that plan and its observed
status without treating it as the form of every useful result.
External execution, publication, installation of other software, provider use,
or runtime action remains separately governed.

The configured result may also preserve one optional owner-specific integration
handoff. It carries the active object, desired result, relevant sources,
retained unknowns, expected contribution, exact effect boundary and return
relation. It is stored only when useful, never in the deterministic installer
plan and never as raw conversation. Pertinent competences may then act alone or
in composition without rebuilding the whole setup conversation.

## State

`setup/CONFIGURATION_STATE.json` is the single project-configuration state owner.
`project/CURRENT_STATE.md` is its compact human projection and
`project/PROJECT_BRIEF.md` is the readable configured result. Update them in
one coherent movement when future behavior or reentry changes. Do not preserve
the raw conversation.

An accepted update also derives `.maios/context/CONTEXT_CAPSULE.json` and
`.maios/context/SETUP_SPEC.json` from the canonical state. The capsule binds
revision, intent, authorized sources, operational dynamics, roles, boundaries,
host, delivery, requested faculties, unknowns, and review. The SetupSpec binds
the capsule and configuration hashes and exposes any missing consequential
decision. Neither projection becomes a second state owner.

When a terminal result is applied, the derived capsule also links a
bounded summary of `.maios/context/OPERATING_CONTEXT.json`: its causal currency,
eligible and blocked local movements, uncertainty count, and authority ceiling.
The operating context is invalidatable and never replaces configuration, host,
competence, faculty, or operating-history owners.

Use `apply-configuration` when a selected configuration change needs its
coupled state and projections updated. It checks the candidate internally;
`validate-configuration --candidate <json>` is available to inspect an input
without applying it. Application requires the exact current-state digest, creates a project-local backup and
receipt, regenerates every projection, and makes no global or external write.
`recover-configuration` refuses recovery if the canonical state evolved after
the receipt.

### Runtime field representations

`faculty_composition.last_readback` links configuration to the last committed
resultant event. It is initially `null`; `apply-resultant` writes an object with
`event_id` and `receipt` (`.maios/receipts/resultant/<event_id>.json`). Ordinary
configuration updates preserve this reference. Narrative configuration summaries
belong in `checkpoint.summary`; they are not event references.

The arrays in `possibility_field` and a resultant's `possibility_impact` accept
nonempty strings or structured objects, including reasons and source context.
Merging and elimination compare complete values, so a structured possibility
keeps its information and is removed by supplying that same value.

Status commands report invalid configuration without applying changes. Recovery
can restore a valid backup even when an older validator accepted the current
invalid state, provided the receipt still matches that exact state.
