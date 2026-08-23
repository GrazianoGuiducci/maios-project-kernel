# Provenance and reproducibility

## Release source

The public repository imports the exact published package archive from:

```text
source owner: MAIOS product source
source state: committed release snapshot
source revision: 7bbc167e4953c133adc1cecb056c88f93f263643
package version: 1.4.0
source archive SHA-256: 6989862fe521d58958588079f7af5e97e276bf976e31714193aceab52ea68234
```

The imported payload contains 64 files and matches the committed source archive
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
64-member source archive checksum above.
