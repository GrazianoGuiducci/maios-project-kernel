# 4.1.2 source and distribution evidence

The maintained generated selection retains method corpus
`3ca6ec85e80fbc69838d4a063a81edb079b2803c` and compiler
`334a9d33c12d61ba826d41b25f604af18441e967` / 0.4.0.dev5.
No selected method is renewed by this release.

Two focused tests exercise the package CLI without an explicit mode on absent,
empty and clone-containing targets, installation and idempotent reapplication,
existing instructions that conflict, and target changes after preview.
The tests pass with the original plan, conflict and recovery mechanics retained.

Local validation exercised 111 tests with two platform skips; all installation
and runtime tests passed. The initial documentation mismatch was resolved by
rebuilding and normalizing edited templates; its five checks then passed.
The ordinary build and inventory verifier pass with 62 files, 51 in the payload.
Generated skill and kernel Markdown bodies match the preceding package exactly.
Details are recorded in CURRENT_STATE.md.
The immutable release commit's workflow checks the same distribution on Linux
and Windows. Receiving-model behavior and existing-project migration are not
established by those checks. The user's original installation is unchanged.

## Post-release verification follow-up — 2026-09-12

Release-time validation above describes the local evidence available when
`8bd762e045cebccffd7139ec8ec12382125b51e6` was published as 4.1.2.
The [tagged workflow](https://github.com/GrazianoGuiducci/maios-project-kernel/actions/runs/34718109257)
subsequently failed and remains historical failed evidence. Its linked-organ
boundary test expected an exception on every status read; the repaired reader
can instead return a structured invalid/recovery refusal with no eligible
resultant action. The local Windows run had skipped that symlink case.

Test-only correction `1f70305fd5358c4b8f1bb2488c0fee3f16866268` accepts the
specific confinement exception or checks that structured refusal, its link
diagnostic and blocked action. Revision
`0bd51e1228760f5d75ae0d746c524b834c7f3154` then refreshes source provenance
and the inventory entry required because the builder fingerprints tests too.
Its [successful follow-up workflow](https://github.com/GrazianoGuiducci/maios-project-kernel/actions/runs/34718811672)
verifies the corrected source on Linux and Windows. It does not turn the
failed tagged run into a passing run.

The release tag, published assets and installed 4.1.2 payload remain unchanged;
these follow-ups change the test contract and generated source identity only.
