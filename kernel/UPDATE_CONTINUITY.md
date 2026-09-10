# Preserve project evolution when the source changes

This is the update method of `maios-project-system`, exercised with competence
formation and host adaptation when an update is selected. An upstream version
is a source of possibilities; it does not replace this project's knowledge,
context, identity or locally learned methods.

The first installation carrying this standard records an `update_baseline` in
`.maios/receipts/install/CURRENT.json`: exact package identity, installed file digests,
source-to-destination relations and configuration/operating schema identities.
The baseline describes distribution, not the current meaning or quality of
evolved local files. Keep the originating artifact or its exact recoverable
source available when a later comparison needs the original bodies.

The receipt also preserves `install_plan`, bound to its original plan digest.
The installed installer `verify` command reports baseline consistency against
that plan and package identity separately from present file evolution. Missing
or inconsistent baseline fields make verification invalid; a locally learned
body can still be reported as `target_evolved` with a valid historical base.
This is an internal consistency check, not a signature against coordinated
rewriting of the plan and receipt. It does not prove that an update was applied.

The same receipt validator derives the file ownership and backup maps from
the original plan. Verification, receipt loading, reapplication and uninstall
use that relation. An inconsistent map stops recovery or reapplication before
changing files or discarding the receipt; an intact baseline alone cannot
establish which paths those operations may change.

For an interrupted installation, `PENDING.json` v3 keeps the original plan
separate from actual creation records. Recovery validates the whole journal
and compares creation-time file identity and content before removal. A planned
file with identical bytes can still belong to another writer; unrecorded or
uncertain provenance requires preservation, including backups. If the same plan
already has a valid committed installation receipt, only the pending journal
is cleaned up. The original plan explains intended effects; recorded creation
and present identity supply the additional evidence needed for recovery.

The initial state contracts are `maios.configuration-state.v3` and
`maios.operating-state.v3`, retained in `maios.installation-receipt.v3`.
Their identities distinguish the new required structures from earlier shapes.
Use these exact identities when reasoning about a later update's compatibility.

When an update becomes useful, understand the functional difference with the
current project. Compare the exact distributed base, the living local body and
the proposed upstream source. Preserve local additions and still-useful
learnings; a newer date is not supersession. A changed context may warrant an
adaptation or selective knowledge transfer instead of a whole-package update.

For the selected local effect, prepare the concrete path and semantic changes
through the owning competences. Resolve changed state contracts before applying
a structural update. Preserve before-images for affected files and the current
configuration, learning state, discovery entries and recovery method. Recheck
the exact affected content before replacing it so concurrent work is retained.
When an overlap needs a semantic decision, form the owner-native merge and
preserve its reasons; do not force an automatic overwrite.

After applying a selected change, follow the learned method into the actual
consumers, including native entries and references. Verify the affected
mechanics and useful continuation, and retain the applied source identity,
local adaptation, new baseline and recovery relation. If the result is partial,
preserve that distinction rather than advancing the whole baseline.

The installer still handles fresh installation, exact-artifact reapplication
and conflict-preserving recovery. It is not a cross-version merge engine.
This standard begins with the release that carries it; no migration adapter
for earlier installations is presumed. There is no updater, scheduler, remote
write or background execution implied by source contact or this method.

## Keep a light source contact

At an ordinary active reentry, use `maios.py source-contact-status` when the
source-contact relation is pertinent. Its durable owner is
`setup/CONFIGURATION_STATE.json#source_contact`. With no recorded attempt, or
when seven days have elapsed since the last attempt, inspect the canonical
[MAIOS Project Kernel repository](https://github.com/GrazianoGuiducci/maios-project-kernel)
in read-only mode for changes that can improve this project's Kernel,
competences or capacity to evolve. Begin with the installed identity in
`.maios/SOURCE_MANIFEST.json`, then the repository `VERSION.md`, `CHANGELOG.md`
and current Release; read deeper only when a material useful relation appears.
If the source is unavailable, continue ordinary work and leave the check
pending without blocking the project.

Treat upstream changes as source-qualified improvement possibilities, not
update commands. Preserve project-owned evolution, report a useful delta to
the operator and let a separately selected local improvement or future update
movement own any material effect. Never download, install, overwrite, migrate
or contact third parties by implication. Record every completed contact,
including one with no useful difference, through `maios.py record-source-contact
--observation <project-local-json> --expected-state-sha256 <configuration-hash>`.
The observation contains `observed_at` (timestamp with timezone), `status`
(`observed` or `unavailable`), `source_identity` (exact observed revision, or
null when unavailable), and a short `summary`. The status command supplies the
current configuration hash. Recording uses the existing configuration owner
and its recovery; it performs no network action.

`last_attempt` preserves the current outcome; `last_success` advances only for
an observed source. An unavailable source remains pending and does not become
a successful refresh. The ordinary cadence prevents repeated identical
attempts at every boot; a changed access condition or a material source signal
can make an earlier contact useful. No background process or mandatory startup
check is created. Continue ordinary work after recording the compact result.

## Return useful experience upstream

Source contact is bidirectional only when real use has produced something worth
returning. A first meaningful use can expose valuable evidence before seven days
have elapsed; a later source-contact reentry is also a natural point to notice
whether accumulated experience contains an informative difference.

Useful return material can include:

```text
first impression that changes understanding of entry or usability;
repeated friction or avoidable latency;
missing or misleading context;
a failure or unsafe/unclear boundary;
an unexpectedly successful behavior worth preserving;
a new possibility made visible by using the Kernel;
a concrete source correction supported by observed evidence.
```

Do not manufacture feedback merely because a source-contact check occurred.
When a useful observation exists, prepare a compact **Evolution Feedback** that
separates installed/source identity, host or coder, goal, observation, evidence,
uncertainty and suggested improvement. Show the public-safe form to the operator
and ask for explicit consent before sending anything outside the project.

With operator consent, observed feedback belongs in a GitHub Issue on the
canonical MAIOS Project Kernel repository, using its `Evolution Feedback`
template when available. A concrete source correction belongs in a fork and a
focused Pull Request. Do not infer direct write authority over upstream `main`,
and do not publish private project contents, credentials, client material,
personal data, private logs or hidden runtime state.

If the current host cannot create a GitHub Issue or Pull Request, return the
prepared feedback to the operator instead of claiming submission. A submitted
report is evidence for the upstream maintainers, not authority to change either
the public Kernel or this project. A later upstream change can return through
the ordinary source-contact relation above.
