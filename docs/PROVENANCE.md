# Provenance and reproducibility

## Release source

The public repository imports the exact published package archive from:

```text
source owner: MAIOS product source
source state: committed local release candidate; publication pending
source revision: d5599a6442c4cfdfb6ac50be252305b955ee8ff9
package version: 1.5.0
source archive SHA-256: 720480a7e4d56b4c182c10705ce0de6786a593666a4433ba1c07c582cbb1e9d5
```

The imported payload contains 66 files and matches the prepared source archive
member-for-member and byte-for-byte. It excludes uncommitted workspace files.
The bounded compiler inputs used during generation are retained outside the
installable payload as `docs/source-manifest.json` and
`docs/project-model.source.json`.

## Generated-output boundary

The package declares `contains_repokernel_source: false`. A pre-publication
hash comparison found no byte-identical file shared with the checked
RepoKernel, d-nd-seed, or d-nd-ux-ai-seed working trees.

This evidence supports source separation; it is not a general legal opinion
about every possible future contribution. New releases must repeat the
provenance and private-residue checks.

## Reproducible archive

`tools/build_release.py` sorts paths, fixes ZIP timestamps, normalizes the
archive root, and adds the repository's license and third-party notice to the
installable payload. Running it twice against the same commit must produce the
same SHA-256.

Because the GitHub release asset adds `LICENSE` and
`THIRD_PARTY_NOTICES.md`, its checksum is intentionally different from the
66-member source archive checksum above.
