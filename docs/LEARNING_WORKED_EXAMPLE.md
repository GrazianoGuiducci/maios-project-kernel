# When a learned method changes the next import

An agent helps a team import supplier records. A required `record_id` column
exists, but one row has no identifier. Checking the header alone accepts that
row. The useful correction is to inspect values as well as columns and teach
that distinction to the project's data-import competence.

This worked example follows that correction into a different import, where
numeric zero is a valid identifier. It uses the existing MAIOS Project Kernel
5.1.0 contracts. The scenario is illustrative; the accompanying
[walkthrough](examples/learning_walkthrough.py) exercises local state transitions
and deterministic sample validators, without a receiving LLM or a supplier system.

## Locate the cause before choosing the change

The same rejected import does not determine the same cause. Ordinary work may
supply enough evidence to distinguish these situations:

| Situation | Evidence that could support it | Useful change |
| --- | --- | --- |
| The required knowledge is absent from the inspected sources | The reachable method teaches header checks but no check of required values | Acquire the distinction and deepen the existing data-import body |
| The knowledge exists but was not recovered | A prior body teaches value checks; the current entry points elsewhere and an attributable access record shows that route | Reconnect the entry to that knowledge |
| The method was available and understood but displaced during work | A recorded account correctly explains the value check, while the produced validator checks only headers | Correct that use; preserve the reusable cause in the responsible method or routing owner |
| The record does not distinguish the causes | A bad output and a missing access log, without enough coverage of the work | Preserve the uncertainty and inspect only what can resolve it |

These are source-bound diagnoses, not automatic classes. A read log establishes
access, not influence. A missing log does not establish nonuse. A remembered
explanation or the agent's account can support an interpretation while leaving
its internal cause unknown. No new diagnostic form is required.

The distinction is already owned by
[competence formation](../skills/maios-project-competence-formation/SKILL.md#competences-as-living-sources-of-awareness).
The example develops the first situation; it does not treat all failures as
missing knowledge.

## Change the method and preserve its source relation

In import A the illustrative records are `{"record_id": "A-1"}` and
`{"record_id": null}`. A header-only validator accepts both. A first revision
rejects false values and therefore rejects the second row. That sample result
supports the narrow observation that the revised validator handles these two
records. It does not establish that every false value is a missing identifier.

The agent changes `skills/data-import/SKILL.md` with the method, reason, scope
and unresolved cases. This is project-owned illustrative knowledge, not a new
preinstalled MPK competence. If coupled operating state also needs continuation,
a resultant can carry a learning delta with these existing fields:

```json
{
  "owner": {
    "kind": "competence",
    "id": "data-import",
    "owner": "skills/data-import/SKILL.md"
  },
  "what_happened": "Import A accepted a row with a null record_id.",
  "causal_delta": "Inspect required values as well as column presence.",
  "why_it_matters": "A present column does not establish a populated record.",
  "future_behavior": "Check each required value; the first false-value rule remains provisional.",
  "source_refs": ["project/import-requirements.md", "project/import-A.json"],
  "activation_relations": ["data_import"],
  "invalidator": "A valid identifier is rejected or a missing identifier is accepted.",
  "reentry_condition": "A later import needs required-value validation."
}
```

This is a `learning_deltas` item, not a complete resultant. The walkthrough
supplies the full
[resultant readback](../schemas/RESULTANT_READBACK.schema.json), including
source positions, actual result, evidence, next movement and causal margin.
Applying it returns a relation ID, called **L1** here, with its own origin and
empty use history. Obtain that ID from the receipt; do not invent it.

Availability, body revision and improvement have different evidence:

| Record or artifact | What it establishes within its scope |
| --- | --- |
| Living method diff, with source and reason | Which reusable knowledge changed |
| Reachable learning relation or optional index entry | Which knowledge can be recovered or recalled |
| Recorded source access | Which source was accessed |
| Receiver's competence footer | Correctable self-attribution of participation |
| Input, executed validator, output and attributable readback | What handling occurred in that case and how it relates to the method |
| A receipt with coherent digests | The recorded local transition; not the truth of every submitted explanation |
| Later relevant work with a different input and attributable outcome | Evidence for use, revision or improvement in that situation |

Preserve who supplied each observation or correction and which source revision
it refers to: a supplier statement, an operator decision, an AI inference or
an attributable joint conclusion. The existing `source_positions` separates
operator sources, evidence, inference and unknowns; referenced project sources
carry the detail and the method's scope. An author name or URL alone does not
validate the lesson, and a joint conclusion does not make its supporting
observations independent.

When recording an inferred explanation, keep it in `source_positions.model_inference`
and preserve unresolved alternatives in `retained_unknowns`. The contracts do
not turn a plausible cause into a proved cause merely because it was saved.

## Let a different case disagree

Import B permits numeric zero and supplies identifiers `0`, `"  "` and `null`.
The first false-value rule rejects zero but accepts whitespace. Its invalidator
has been met. Record the outcome, correct the working body, and qualify the
rule: a value is missing when it is null or a string empty after trimming;
numeric zero is accepted under this import's requirements.

A later use of L1 names its ID in `movement.selected_faculties`, explains its
contribution in `faculty_deltas`, and cites the actual case evidence in
`actual_result.evidence_refs`. Selection alone does not record a later use:
the faculty delta supplies the use description. A failed or mixed result can
be informative use; it must not be labeled an improvement by default.

The new learning delta explicitly sets `supersedes: [L1]` and explains the
`supersession_reason`. The resulting **L2** has its own origin and empty use
history. L1 retains its earlier use evidence and the edge to L2; that evidence
is not transferred as proof of L2. Plural or cross-owner continuation can use
the existing `supersession_context` relation and sources when required.

Import C uses the corrected method on different records, including string
`"0"`, an empty string and whitespace. Preserve the inputs, method revision,
output and the relation to the requirement. A real receiving-agent observation
could then support an improvement claim limited to that handling. The
walkthrough instead executes a prescribed validator and supplies fixture
readbacks: it demonstrates how the records work, not that an LLM learned the rule.

The runtime's `later_nonidentical_use_observed` flag compares the recorded
circumstance digest with the origin digest. A changed digest alone cannot
decide whether the situation is meaningfully different or whether learning
caused the outcome. Judge that relation through the actual work. Evidence
references and classifications are supplied claims, not an automatic semantic
verification service.

## Preserve when it happened and when it became known

Consider a separate illustrative requirement change:

| Time | Occurrence or available understanding |
| --- | --- |
| Monday, 5 October | The supplier changes its required fields, according to a dated supplier source |
| Tuesday, 6 October | The agent processes an import using the previously acquired requirements |
| Thursday, 8 October | The project receives the change notice and can correct its current requirements |

Keep the supplier's event date and the project's acquisition date with their
respective evidence in the existing requirement source or continuity note.
The Tuesday result keeps its then-consumed source identity and understanding.
Thursday's readback points to the new source and explains what now changes.
Acquisition later does not make the earlier agent knowingly ignore the change;
an absent acquisition record may leave that question unresolved.

`observed_at` names the observation recorded in a resultant. It is not a
built-in pair of event-time and knowledge-time clocks. The open `source_positions`
object can carry qualified temporal context or point to the source that owns
it. The current runtime preserves the submitted readback but does not verify
clock provenance or infer these dates. No new schema is needed to retain the
distinction. [Knowledge continuity](../kernel/KNOWLEDGE_CONTINUUM.md#preserve-the-movement-before-context-is-lost)
and [FDLA](../skills/maios-project-system/references/fdla-operating-knowledge.md#recompose-when-a-consequence-changes-understanding)
own its operating meaning.

## Retire or reopen the right object

| Object | Existing operation | Separate work still needed |
| --- | --- | --- |
| Learning relation | `learning_transitions` with exact `relation_id`, `status`, `reason` and `reentry_condition` | `cooled` or `retired` removes automatic candidate recall; it does not edit the body |
| Successor learning | New delta with `supersedes` and `supersession_reason` | Teach the new method to the actual knowledge owner |
| Optional competence index entry | `maios.competence-delta.v2` with `revise`, `supersede` or `retire` and the current `supersedes_event_id` | Reconcile living body, native entries and any remaining routes |
| Earlier knowledge body | A source revision through its owning competence, preserving the reason and history | Reopening a learning relation does not restore those bytes |
| External import or other effect | Its actual controller and action-specific authority, evidence and recovery | A local learning or index receipt cannot undo that effect |

Learning relation IDs and competence-index event IDs are different identifiers.
An optional index admission is not a mandatory promotion stage before knowledge
can be used. An `evaluate` disposition leaves an index observation in history
without activating the entry; it is available when that is the useful choice.
Retirement does not physically delete knowledge or guarantee that every host
route has stopped using it.

## Run the contract walkthrough

From the source repository with Python >=3.11:

```text
python -B docs/examples/learning_walkthrough.py
```

The script builds and installs into an automatically cleaned temporary
directory. It checks availability before use, records L1's later use and
supersession, gives L2 its own use history, retires and reopens L2, and verifies
that the predecessor evidence survives. It changes no existing installation,
repository package, host configuration, account or external data. All learning
classifications remain `unverified`; the observations are explicitly fixtures.

The returned JSON summarizes sample-validator results and local receipt
relations. It is mechanical evidence for this example, not model assimilation
or a reported field trial. A real trial would retain its own source/body
identities, coverage, outputs, receiver account and unresolved causes.

## Why this example was added

The public discussion on 6–7 October distinguished missing knowledge, failed
recovery and displaced use, and asked how later behavioral change could remain
attributable and revisable. Serreth identified existing source passages and
explicitly said MAIOS had not been tested in their collaboration. Daareek
asked about provenance and reversible promotion. These are questions and
comparative observations, not MAIOS test results.

The [6 October source discussion](https://community.openai.com/t/ai-as-a-tool-an-automation-platform-or-a-long-term-collaborator-are-these-becoming-different-products/1403250/8),
[lifecycle question](https://community.openai.com/t/ai-as-a-tool-an-automation-platform-or-a-long-term-collaborator-are-these-becoming-different-products/1403250/9)
and [7 October response](https://community.openai.com/t/ai-as-a-tool-an-automation-platform-or-a-long-term-collaborator-are-these-becoming-different-products/1403250/10)
remain attributable to their authors. This example supplies a public reading
and reproduction path for the existing contracts; it adds no runtime feature
or new required workflow. See [cultivation](../kernel/COMPETENCE_CULTIVATION_PROTOCOL.md),
[receipts](RECEIPTS.md) and [5.1.0 trace limits](RELEASE_5.1.0.md#a-trace-the-person-can-read-and-correct)
for the owning definitions.
