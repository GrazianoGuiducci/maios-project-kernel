# Product version

Product version: `5.1.0`.
Project Kernel family: `3.0.0` (unchanged).
Previous public product version: `5.0.0`.

This minor version adds a receiver-local competence trace and makes endogenous
receiver qualification explicit through existing competence formation. The
autonomous family source now distinguishes required context from a discretionary
interview, matching the semantics already delivered in 5.0.0.

Installation and local helpers require Python >=3.11; qualified support covers Python 3.11–3.14
on Linux, Windows and macOS. Newer Python versions and other architectures are
not implicitly qualified by this matrix.

Family 3.0.0, runtime, installer/recovery, state schemas, host contracts and the
support matrix retain their compatibility. Reapplying the
same artifact is idempotent; this does not supply automatic migration between
product versions. See [release content](docs/RELEASE_5.1.0.md) and
[installation and recovery](docs/INSTALLATION.md).
