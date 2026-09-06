# MAIOS Project Kernel 3.1.2

This patch corrects the six persistence and path-confinement findings from the
review of 3.1.1. The previous release remains an immutable baseline.

- Event IDs cannot alias the PENDING control file, including case equivalents.
- Host and competence state use the same caught-failure rollback and recovery
  evidence as configuration and resultants. Missing receipts cannot become
  successful idempotent retries.
- All atomic JSON, text, bytes and restore writes acquire their temporary
  exclusively, write through its descriptor and clean only its qualified
  identity. Foreign files, hardlinks, symlinks and replaced temporaries survive.
- The installer and runtime share local path confinement, including junctions
  through Windows reparse metadata available on Python 3.10.
- Terminal receipts are checked against their own body, digest, event and
  history. Historical replay remains valid after legitimate later evolution;
  it does not re-evaluate old movements against today's semantic field.
- Installer verify explicitly reports `verification_scope: installer_owned_files`.
  Current kernel structure remains the separate scope of `maios.py status`.

The suite contains 77 cases, eleven new. Local Windows passed 75 and skipped
the two symlink-creation cases; the real junction case passed. CI covers Ubuntu
with Python 3.10 and Windows with Python 3.10 and 3.13. Read the exact release
commit's CI for observed results. The package contains 60 files, 49 payload;
the same filesystem source is projected into both standalone import contexts.

The changes address ordinary caught failures and pre-existing local path
collisions. They do not introduce a general concurrent-writer lock, automatic
journal replay, multi-file crash-safe commit or cryptographic authenticity.
Journals remain evidence for qualified recovery. Python's
[mkstemp contract](https://docs.python.org/3.10/library/tempfile.html#tempfile.mkstemp)
and [reparse metadata](https://docs.python.org/3.10/library/stat.html#stat.IO_REPARSE_TAG_MOUNT_POINT)
qualify the underlying platform mechanisms.

The family stays 3.0.0. There is no automatic cross-version migration. Native
model use and later non-identical assimilation remain separate unobserved
claims. Form, site and unified chat/harness retain their receiving owners.
The installable projection is the tracked `package/` directory.
