# MAIOS situated configuration contract — canonical source

Configuration makes the package specific to the present person, project,
domain, sources, and host without deciding a solution form in advance.

This archive is the `self_configuring` entry. It does not import Form state,
P1-P5 answers, a Terminal Context Field, or an accepted external case. A Form
route may later converge on the same situated-project function, but remains a
different temporal source and builder until independently compared.

## Result

The first useful configuration preserves:

- the person's current intent and point of view;
- the real work, problem, or desired change;
- facts, hypotheses, contradictions, unknowns, and source references;
- possibilities with reasons, smallest proof, invalidator, and reentry
  condition;
- the selected or still-open direction and its review state;
- the result to produce, beneficiary, value mechanism, smallest deliverable,
  and falsifiable first proof;
- people, responsibilities, environment, and observed host capabilities;
- the project-local data boundary, private fields, any explicitly allowed
  external projection, and provider consent kept separate from project intent;
- the selected faculty composition and why every faculty changes the movement;
- exact effect authority, which remains `none` until an effect actually exists.

## Interaction

Read the current request and project files before asking questions. Return what
is already understood and a correctable useful movement. Ask only when one
missing relation would materially change meaning, owner, result, proof, safety,
or next movement. Unknowns that do not block the first useful result remain
explicit and are revisited during work.

Do not expose internal schemas, faculty names, or architecture when they do not
help the person's decision. A request to shorten or stop questions changes the
interaction, not the semantic review of the proposed direction.

## Completion

Configuration becomes `configured` when the project has a concrete case,
first useful result, attributable sources, selected
movement, and recoverable reentry. It does not require every unknown to close.
External execution, publication, installation of other software, provider use,
or runtime action remains separately governed.

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

When deterministic support is available, use `python maios.py
validate-configuration --candidate <json>` before `apply-configuration`; apply
requires the exact current-state digest, creates a project-local backup and
receipt, regenerates every projection, and makes no global or external write.
`recover-configuration` refuses recovery if the canonical state evolved after
the receipt.
