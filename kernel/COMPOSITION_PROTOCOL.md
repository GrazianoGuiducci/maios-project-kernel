# Situated composition protocol — canonical source

The semantic host owns interpretation. Deterministic projection only exposes
known candidates and validates the declared movement; it does not decide which
meaning or faculty is correct.

## Entering field

Recover only relations that can change the movement:

```text
accepted intent and requested result
present object, sources, actors, and unknowns
host capabilities actually observed
current project state and reentry
material effect, if one exists
relations exposed by the emerging result
```

## Composition

1. Keep permanent source/aperture and self-correction relations silent.
2. Use the current circumstance to project known candidate families.
3. Include project-local learning relations only when their activation
   relations match the current circumstance; keep persistence distinct from
   later assimilation evidence and the separately governed competence index.
4. Exercise only candidates with a stated expected delta.
5. Admit an unmatched material relation as a sourced extension instead of
   forcing it into the nearest family.
6. Reroute when the circumstance or resulting state changes.
7. Stop when another pass changes no material relation.

`python maios.py compose --circumstance <json>` returns the represented portion
of this field. A selected movement may be checked with `validate-movement`.
`operating-status` then exposes the current capability relations, causal input
digests, invalidations, uncertainty, and project-local actions that remain
eligible. It is a current projection, not a semantic router or permission.

## Movement record

```json
{
  "circumstance": {
    "requested_result": "...",
    "relations": ["context_indeterminate"],
    "effect": null
  },
  "selected_faculties": [
    {
      "id": "field-illumination",
      "reason": "...",
      "expected_delta": "..."
    }
  ],
  "effect_boundary": null
}
```

For an extension add `source_refs`, `invalidator`, and `reentry_condition`.
Validation proves contract shape only; behavioral readback proves whether the
composition actually helped.

## Terminal readback

After inspecting the resultant, record actual status and classification,
faculty deltas, source positions, possibility impact, next movement, effect
state, and an optional owner-bound learning delta. Use `validate-resultant`
before `apply-resultant`. Application is the terminal project-local coupling
from the observed result to configuration, evolution, operating state,
projections, learning, and reentry. If its operating-context hash is stale,
re-read the current field instead of merging over changed causal inputs.

When a causal learning delta exists, the next movement must carry one of its
activation relations. The relation becomes reachable at once; a later selected
exercise records non-identical use without manufacturing an admission or
claiming assimilation. External claims and effects still resolve their exact
evidence and authority where they arise.
