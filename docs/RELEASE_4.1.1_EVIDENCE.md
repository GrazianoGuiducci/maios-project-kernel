# 4.1.1 source and distribution evidence

The source increment begins at candidate `0d9b58fff0399c092a570e339a24f61701e4fa2b`.
The compiler is pinned to `334a9d33c12d61ba826d41b25f604af18441e967` / 0.4.0.dev5.
The final selected source commit and plan hash are recorded in
`release/GENERATED_KERNEL_SELECTION.json`; generated methods preserve exact
normalized source bodies and the package inventory identifies delivered bytes.

Candidate CI passed its 101 source tests. Its builder returned valid; the
subsequent Git comparison failed on changed manifest/inventory hashes. That
failure did not detect the absent feedback method in the old retained selection.
Production acceptance therefore checks the delivered system and update methods
against their native sources, in addition to ordinary distribution verification.

No receiving-model use, real feedback submission or installed-project migration
is claimed by these mechanical checks. The historical entity-profile input is
unchanged and remains separately identified by the manifest.
