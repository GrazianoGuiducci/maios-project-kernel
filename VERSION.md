# Product version

Product version: `5.0.0`.
Project Kernel family: `3.0.0` (unchanged).
Previous public product version: `4.5.0`.

The major version records the removal of Python 3.10 support. Installation and
local helpers require Python >=3.11; qualified support covers Python 3.11–3.14
on Linux, Windows and macOS. Newer Python versions and other architectures are
not implicitly qualified by this matrix.

The family, local state and receipt contracts remain unchanged. Reapplying the
same artifact is idempotent; this does not supply automatic migration between
product versions. See [release content](docs/RELEASE_5.0.0.md) and
[installation and recovery](docs/INSTALLATION.md).
