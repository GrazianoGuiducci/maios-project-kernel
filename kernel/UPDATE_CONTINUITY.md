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
