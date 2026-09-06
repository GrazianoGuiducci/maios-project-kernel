# Receipt claim levels

The installer writes its current receipt under `install/`. Host, behavior, and
reentry receipts belong here only after the exact state is observed. A receipt
must name artifact identity, target, claim level, evidence, non-claims, and
recovery. Do not prefill success.

Terminal resultants are applied under `resultant/<event_id>.json`.
Their receipt binds the readback digest, before/after operating and
configuration hashes, operating-context hash, nested configuration receipt,
and explicit non-effect claim. It proves the deterministic local transition
only; optional classifications need their referenced evidence, and any
external effect requires its own terminal receipt.

A resultant receipt may name several created learning relations and any
older relations exercised by that movement. These fields prove only the
project-local causal transition. Reachable learning remains under
`.maios/state/OPERATING_STATE.json`; it is not itself proof of assimilation.
Only a separate competence receipt can prove an owner-governed competence-index
change, and neither receipt alone proves maintained behavior.

Learning receipts may preserve multiple distinct aspects of one owner.
Supersession names exact predecessor IDs and reasons. Earlier use remains
attributed to that relation; it is not inherited as evidence about a successor.
`learning_transitions` preserves cooling, retirement or reopening of a named
relation with its reason and reentry. These records do not themselves edit
semantic knowledge bodies. Installation receipts include `update_baseline`
with source/destination identities and the initial distributed hashes.

Learning relation v2 carries plural historical `superseded_by` references and
an event-bound `lifecycle`. These remain after reopening a predecessor; its
current status controls recall. A `supersession_context` object, with an open
`relation` description and `source_refs`, qualifies cross-owner or further
plural continuation. Current status, owners, reference symmetry, event order
and use evidence are validated when reading the operating state.

Resultant receipts preserve `consumed_knowledge_refs`; operating state keeps
the current `active_knowledge_refs` for a fresh default reentry. Omission
inherits that selection and an explicit list replaces it, including `[]`.
An install receipt retains its original `install_plan`; verification compares
the update baseline against this digest-bound plan and package identity.
The canonical receipt validator also derives all owned files, preserved
pre-existing paths, the backup root and backup files from that same plan.
Receipt readers, idempotent reapplication and uninstall consume this validator.
An inconsistent current receipt blocks reapplication and uninstall before any
mutation, preserving both project files and the receipt for recovery.
Verification cannot claim `installed` or `valid` from an untrusted file map;
`receipt_validation` explains the inconsistency. With a valid receipt, file
presence and local evolution are reported separately. Local evolution does not
invalidate the historical baseline.

The first-user contracts are `maios.installation-receipt.v3`,
`maios.configuration-state.v3` and `maios.operating-state.v3`. Their required
original plan, source-contact/provenance and knowledge-selection/genealogy
structures differ from the earlier v2 shapes. Learning relations retain their
own `maios.learning-relation.v2` identity. This names the new contracts and does
not introduce a migration for earlier installations.

Interrupted existing-project installations use `maios.pending-installation.v3`.
Its original `install_plan`, digest and package/target identity bind the complete
`planned_files` and `planned_backup_files` maps. `created_files` separately
records successful exclusive creations, each with its planned hash and the
device, inode and qualified timestamp observed on the creating descriptor.
Use birth time when available, otherwise metadata-change time, retaining that
basis in the record. Python distinguishes these platform-dependent attributes
in its [stat documentation](https://docs.python.org/3/library/os.html#os.stat_result).
A missing reliable identity remains explicitly uncertain. An attempt UUID and
exclusive journal creation keep a failed acquisition from recovering another
attempt. These records are local evidence, not signatures against coordinated
rewriting of the journal and its sources.

The pending validator rejects the entire inconsistent journal before deletion.
Recovery compares recorded file identities and hashes with the present files;
planned paths alone never authorize deletion. Uncertain or changed files and
their journal remain available. A matching committed installation receipt
changes recovery into journal cleanup only. Recovery reports this as
`maios.pending-installation-recovery.v3` with `installation_retained`.

Installer `verify` reports receipt consistency and the current files recorded
as installer-owned. Pre-existing identical target-owned files are preserved
but not included in that file report; `maios.py status` checks the current
required Kernel structure through its canonical state readers. Neither command
certifies semantic use or assimilation by a model.

A valid historical receipt for a target is not authority over every later
installation at that path. Uninstall compares it with a valid CURRENT before
its first deletion, including for explicit `--receipt` use. Target, original
plan, digest and package identity must agree. Missing or invalid CURRENT, or a
different current plan, refuses uninstall without changing files.

Read-only verification keeps `receipt_validation` and `files_present` separate
from `current_relation` (`current`, `current_mismatch`, `current_missing`,
`current_invalid`). Overall `valid` and `installed` require both historical
consistency and the current relation. This is plan identity, not a signature or
a lock against arbitrary concurrent writers.

Existing-project receipts do not record directory ownership. Uninstall retains
empty parent directories after file, backup, cache and receipt cleanup. New
repository mode retains its existing empty-parent cleanup inside the target.

Runtime configuration, resultant, host and competence transitions snapshot the canonical state,
derived projections and prior receipts before their first state write. Their
owner-local `PENDING.json` journals carry base64-encoded original bytes and paths
under `maios.state-transition-journal.v1`. Caught failure restores those exact
bytes, including the prior configuration receipt, independently of whether a
callee returned its new receipt. Failed rollback retains the journal; `status`
and `operating-status` expose recovery needs and another apply is refused.

The journals are recovery evidence, not executable plans. After an incomplete
rollback, inspect the named owner, original bytes and present files and reconcile
the exact affected state before removing the journal. A cleanup-only failure
after a committed transition also leaves that evidence visible. There is no
automatic journal replay, arbitrary-writer lock or multi-file crash-safe claim.
Configuration backups can remain as evidence after a caught failure.

Identical configuration reapplication returns an idempotent result without
changing projections or CURRENT; that result points to the last material
transition receipt. The receipt and its recoverable backup remain linked.
Status and replay share terminal evidence validation: receipt structure, event
identity, body digest and history must agree. Resultant readbacks are hashed
from their stored body; host and competence events keep that body in their
history. Earlier host v2 receipts bind stage, result and revision to the full
digest-bound historical attestation. Historical after-state hashes describe
that transition, not today's state after legitimate evolution. Old semantic
choices are not rejudged against the present field during replay.

PENDING is reserved case-insensitively in all event-owning paths; an event
cannot use a transaction control pathname. A terminal path already present
outside recorded history is preserved and refused. A replay requires coherent
terminal evidence, even when the request is an exact duplicate.

All JSON, text, bytes and rollback outputs use exclusively acquired temporary
files, written through the original descriptor and cleaned only while their
qualified identity remains. Installer and runtime use the same path helper;
Windows junction checks use reparse metadata available in Python 3.10.
Installer verify declares `verification_scope: installer_owned_files`; this
never transfers a pre-existing file to uninstall ownership.

Host and competence event inputs reserve the top-level names `sequence` and
`event_digest` for history metadata. They are rejected before state writes;
other extensions, including nested uses of these names, remain allowed.

Current host and competence-index state must match the latest owner's terminal
receipt: revision, event identity and after-state digest are checked together.
Earlier receipts are validated against their own history, never today's state.
An unrecorded change requires recovery; duplicate input does not repair or
legitimize it. Incoherent host capabilities are reported as unverified. This
does not bind living knowledge-body bytes to an index receipt. Preserve the
affected files and reconcile the exact owner; no automatic repair or proof of
authenticity against coordinated changes is implied.
