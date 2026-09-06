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
