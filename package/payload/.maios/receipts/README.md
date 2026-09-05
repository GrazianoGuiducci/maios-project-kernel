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

A resultant receipt may name one created or revised learning relation and any
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
