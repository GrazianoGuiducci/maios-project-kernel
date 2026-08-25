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
3. Exercise only candidates with a stated expected delta.
4. Admit an unmatched material relation as a sourced extension instead of
   forcing it into the nearest family.
5. Reroute when the circumstance or resulting state changes.
6. Stop when another pass changes no material relation.

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
state, and the independent review. Use `validate-resultant` before
`admit-resultant`. Admission is the terminal project-local coupling from the
observed result to configuration, evolution, operating state, projections, and
reentry. If its reviewed operating-context hash is stale, re-read and
re-evaluate instead of merging over changed causal inputs.
