# Provenance and reproducibility

## Release source

The public repository imports the exact published package archive from:

```text
source owner: MAIOS product source
source state: committed release snapshot
package version: 1.3.0
source archive SHA-256: 45015d338a7a2b7cf7925f072b5204b023dbd78806565f16fb44479f0ad94bd6
```

The imported payload contains 53 files and excludes uncommitted workspace
files. The bounded compiler inputs used during generation are retained outside
the installable payload as `docs/source-manifest.json` and
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
