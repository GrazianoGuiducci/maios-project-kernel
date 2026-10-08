# From recorded learning to observable competence: a worked example

This is an **illustrative walkthrough of MAIOS Project Kernel 5.1.0 contracts**, not an observed user trial, a model evaluation, or a report that the participants in an external discussion tested MAIOS. The project, dates, file paths and example records below are hypothetical. The linked schemas, methods and source tests are real repository sources. No sample receipt below is claimed to have been produced.

## The work before the labels

Imagine a team maintaining an order importer. Its current validation method rejects a row without a customer identifier. On **Monday 5 October**, the team's authoritative import contract changes: guest orders may have no customer identifier when a separate guest-order flag is present. The coder does not receive or consult that changed contract until **Thursday 8 October**. It processes an import on Tuesday using the old method.

Three facts must remain distinct:

- **Occurrence:** the contract changed on Monday; the source's recorded revision or change event is evidence of that occurrence.
- **Knowledge available to this receiver:** the changed contract did not enter the coder's inspected sources until Thursday, assuming the ordinary source-read record supports that account. No trace cannot by itself prove no access.
- **Current interpretation:** on Thursday the team now knows the Tuesday decision should be reconsidered in light of the Monday change. It must not rewrite Tuesday's evidence as though the coder already possessed Thursday's knowledge.

The [knowledge continuum](../kernel/KNOWLEDGE_CONTINUUM.md#preserve-the-movement-before-context-is-lost) preserves event, understanding then and understanding now. The [resultant-readback schema](../schemas/RESULTANT_READBACK.schema.json) has `observed_at` for the readback and distinct `source_positions` for operator statements, verified evidence, model inference and unknowns. **`observed_at` is not a built-in assertion that the underlying external event happened at that time**. Preserve Monday's occurrence time in the source and its reference; preserve Thursday's acquisition/readback separately. Do not invent a new schema field or backdate a receipt to close the gap.

## Three superficially similar failures, three different corrections

| Situated finding | What it actually means | Appropriate response |
| --- | --- | --- |
| The revised validation rule is **not present** in the project's living competence knowledge | Knowledge needed for the work is absent from that owner, once relevant sources have been checked | Acquire and qualify the changed contract; teach the smallest relevant validation competence its method and reason |
| The revised method **already exists** in a living competence, but the receiver did not reach it | Knowledge exists; the entry, routing, discovery or source selection failed | Reconnect the pertinent native entry or retrieval route; avoid duplicating the body as a new skill |
| The revised method was **read or available**, but the import still used the old decision | Access is observable; competent participation or correct application is not thereby established | Examine the decision/output and attribution; correct actual use and, only if reusable, the responsible method or routing relation |

These are diagnostic possibilities, **not a mandatory questionnaire**. A missing tool log is not proof of nonuse, and a source read is not evidence that its method changed a decision. The [formation competence](../skills/maios-project-competence-formation/SKILL.md#competences-as-living-sources-of-awareness) already owns these distinctions.

## Follow one correction through the existing contracts

1. **Qualify the source and the actual decision.** Inspect the authoritative contract version and the Tuesday import result. In `source_positions`, separate operator-supplied source, verified input/output, inference and unresolved access history. A timeout would establish a timeout, not its root cause.
2. **Correct the acting knowledge owner.** If the method was genuinely incomplete, revise the project's *living import-validation competence body* with the guest-order condition, evidence, reasons, and an invalidator. If the body already had the rule, repair its entry or its use instead. Changing a project source file is different from creating a state receipt.
3. **Record a coupled transition only if one is needed.** A `maios.resultant-readback.v3` may describe the actual result, `faculty_deltas`, source positions and `learning_deltas`. This is optional for ordinary knowledge editing; `apply-resultant` is for a selected managed-state transition. The receipt proves its recorded local transition, **not** that the competence body was semantically changed or later used.
4. **Observe a different later import.** A subsequent guest order is a different case from the correction itself. Record the actual input, the validation decision and its sources. A competent self-attribution at response closure can be inspected, but is not independent proof. If the recorded resultant selects the previous learning relation as a faculty and its readback reports a contribution, its `later_uses` genealogy shows **recorded exercise**, while the external input/output still determines what behavioral claim the evidence supports.
5. **Revise without erasing.** If a later contract says guest orders are valid only for one channel, amend the living method and, where a managed learning transition is selected, use `supersedes` plus `supersession_reason` to connect the revised learning to its exact predecessor. The older relation retains its prior use history; the successor starts with no inherited later-use proof. `learning_transitions` can cool, retire or reopen a relation, with a reason and reentry condition. Changing recall status does not itself undo code or an external effect.

For step 3, this is a **field-level illustration**, not a complete, submit-ready event:

```json
{
  "learning_deltas": [
    {
      "owner": {
        "kind": "competence",
        "id": "import-validation",
        "owner": "skills/import-validation"
      },
      "what_happened": "The authoritative guest-order rule became available to the team",
      "causal_delta": "The old rule rejected valid guest orders",
      "why_it_matters": "Future imports must distinguish guest orders from incomplete registered-customer rows",
      "future_behavior": "Check the current contract and guest-order flag before rejecting a missing customer identifier",
      "source_refs": ["docs/import-contract.md"],
      "activation_relations": ["order_import_validation"],
      "invalidator": "The authoritative import contract or later execution evidence changes this rule",
      "reentry_condition": "A new import requires row validation"
    }
  ]
}
```

The paths and values inside this example are **hypothetical**, not Project Kernel product files or observed learning. The complete event requires additional fields in [`RESULTANT_READBACK.schema.json`](../schemas/RESULTANT_READBACK.schema.json). The record above is useful only if the real work, correct owner and real source references justify it.

## Evidence is plural and claim-scoped

| Available evidence | What it supports | What it does **not** support on its own |
| --- | --- | --- |
| Competence body/source and native entry | The method is represented, and perhaps discoverable in that host | The receiver read, applied or assimilated it |
| Source-read or tool-result record | Access or tool occurrence at the recorded time | Causal influence on the decision |
| Compact receiver competence trace | The agent's correctable account of participation | Hidden reasoning or independent behavioral proof |
| Source diff or updated living knowledge | A recorded knowledge-body change | Validity, successful runtime effect or later use |
| Valid terminal resultant/learning receipt | The claimed deterministic local state transition and its retained genealogy | Semantic improvement, external effect or receiving-model assimilation |
| Later, non-identical input/output plus attributable readback | Evidence to assess whether a learned method changed later behavior | Universal improvement across hosts, tasks or conditions |
| `supersedes`, cooling or retirement with reason | Genealogy and current recall disposition | Undo of knowledge files, code, releases or external consequences |

A `verified_improvement` label is a **claim requiring attributable evidence**, not a status automatically earned by schema validation. If evidence is insufficient, retain `unverified`, an unknown, or no stronger classification. The relevant mechanics are in the [cultivation protocol](../kernel/COMPETENCE_CULTIVATION_PROTOCOL.md#forward-resultant-learning), [receipt claim levels](RECEIPTS.md) and [5.1.0 release notes](RELEASE_5.1.0.md#a-trace-the-person-can-read-and-correct).

## Where to inspect without creating a new subsystem

In a genuinely installed, authorized local project, useful read-only inspection includes:

```text
python maios.py knowledge-status --path skills/import-validation/SKILL.md
python maios.py learning-status
python maios.py learning-status --include-cold
python maios.py operating-status
python maios.py audit-continuum
```

The example `skills/import-validation/SKILL.md` path must be replaced with an actual project-owned path. `knowledge-status` inspects named source identities; `learning-status` observes learning availability and history; `audit-continuum` separates current operational and cold-genealogy validity. These diagnostics do **not** themselves certify that a model used the method. See [usage](USAGE.md#project-local-operation).

The actual source tests [`test_learning_coexists_without_forcing_the_next_field`](../tests/test_knowledge_continuation.py) and [`test_supersession_and_cooling_preserve_revision_specific_evidence`](../tests/test_knowledge_continuation.py) assert distinct recorded-use and genealogy behaviors. They are executable contract examples, **not external model or community tests**. Their passing status must be established by an identified run, not inferred from their presence.

## What would falsify an improvement claim?

A later different guest-order import that still rejects a valid guest row, a trace that points to the wrong contract, or a missing owner/body correction can overturn a claim of improvement. An unexpected pass on a different case also needs its actual input, decision and evidence before crediting the competence. If the skill was already correct and only discovery failed, the reusable difference belongs to discovery/routing rather than a duplicate domain skill.

The walkthrough adds **no runtime feature, mandatory telemetry, evidence gate, learning store or new competence**. It only makes existing distinctions readable together. The immutable released 5.1.0 artifact is separate from this source-documentation proposal.
