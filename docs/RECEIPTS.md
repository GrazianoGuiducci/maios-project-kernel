# Receipt claim levels

The installer writes its current receipt under `install/`. Host, behavior, and
reentry receipts belong here only after the exact state is observed. A receipt
must name artifact identity, target, claim level, evidence, non-claims, and
recovery. Do not prefill success.

Reviewed terminal resultants are admitted under `resultant/<event_id>.json`.
Their receipt binds the readback digest, before/after operating and
configuration hashes, operating-context hash, nested configuration receipt,
and explicit non-effect claim. It proves deterministic local admission only;
the referenced observation and review govern semantic quality, and any
external effect requires its own terminal receipt.
