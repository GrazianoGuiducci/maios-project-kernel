# Provenance and reproducibility

## Release source

The public repository imports the exact published package archive from:

```text
source owner: MAIOS product source
source state: committed local release candidate; publication pending
source revision: 9ef21c4622687ae6749644e7d996174b09ac7a43
package version: 1.6.0
source archive SHA-256: fc2c366a49cdbf662201c1fb4c80877bafabc932eaf0788a699a948681aa1982
```

The imported payload contains 69 files and matches the prepared source archive
member-for-member and byte-for-byte. It excludes uncommitted workspace files.
The source manifest is also delivered inside the package. The project-model
input used during generation remains outside the installable payload as
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

The GitHub release builder overlays the repository-level `LICENSE` and
`THIRD_PARTY_NOTICES.md` at the same archive paths. Its checksum may therefore
differ from the 69-member source archive checksum above while the member count
remains unchanged.
