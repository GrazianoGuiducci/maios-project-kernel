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
