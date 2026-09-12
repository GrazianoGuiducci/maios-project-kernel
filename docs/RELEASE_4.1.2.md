# MAIOS Project Kernel 4.1.2

The coder supplies a target folder and host to `install.py preview`, then applies
the resulting plan. Folder handling is automatic: empty targets use atomic new
installation; non-empty targets preserve existing work. The same command works
when the chosen folder already contains the source clone. Explicit modes remain
available, and reapplication retains the original mode for the same package and host.

Installation instructions now lead directly to the installed `START_HERE.md`
and its operating competence. They supply package knowledge without prescribing
a conversation or conflating a non-empty folder with an established project.

This release also includes the previously unreleased configuration repairs:
invalid event references are rejected before writes, diagnostics handle legacy
invalid state, receipt-bound recovery preserves subsequent work, and structured
possibilities retain their reasons through resultant application.

The complete generated kernel selection and Project Kernel family 3.0.0 are
unchanged. This release changes installation, product entry and runtime readers;
it does not regenerate the methods or migrate existing installations.

See [source and distribution evidence](RELEASE_4.1.2_EVIDENCE.md). Mechanical
verification is distinct from the next OpenCode first-use test.
