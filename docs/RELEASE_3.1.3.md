# MAIOS Project Kernel 3.1.3

This patch corrects two owner-event integrity findings from the review of
3.1.2. The six persistence and path-confinement corrections in 3.1.2 remain.

- Host attestations and competence deltas reject top-level `sequence` and
  `event_digest` before writing. Those two names belong to history metadata;
  other extensions, including nested fields with those names, remain open.
- Host and competence-index status, continuum reentry and replay share a
  check linking the current revision and event to the latest receipt and its
  after-state digest. An isolated state or receipt change requires recovery;
  duplicate input cannot turn that inconsistency into an idempotent success.
- Capabilities recorded in incoherent host state are exposed as unverified,
  including in the operating context. Stored state is preserved for recovery.
- Earlier receipts retain their historical meaning after a later admission.
  Competence knowledge bodies can evolve independently of index registration;
  another owner's legitimate transition does not invalidate these receipts.

Six focused regressions exercise both owners through the installed CLI in fresh
isolated processes. The complete suite now contains 83 cases. CI covers Ubuntu
with Python 3.10 and Windows with Python 3.10 and 3.13; consult the exact release
commit for observed results. The package retains 60 files, 49 in the payload.

These are internal coherence guarantees, not cryptographic authenticity against
coordinated rewriting. No automatic repair of previously inconsistent state or
cross-version migration is introduced. The family remains 3.0.0. Native model
use and later non-identical assimilation remain separately unobserved.
The installable projection is the tracked `package/` directory.
