# Source basis for the next generated release

## Maintained renewal from 4.1.0

Use [RENEW_KERNEL_SELECTION.md](RENEW_KERNEL_SELECTION.md) and the exact current
`release/GENERATED_KERNEL_SELECTION.json`. The renewal reads committed product
bodies and invokes the pinned compiler; its selected-corpus identity is distinct
from the current builder's whole-source digest. The current compiler adoption is
334a9d33c12d61ba826d41b25f604af18441e967. The previous consolidation below retains
its historical identity and does not select the current release input.

## Historical consolidation for 4.0.0

The next production input is formed from the current living source corpus,
including the context-method refinement already exercised through generation
and installation. It is not formed by relabeling the earlier published commit
as if it contained the local work.

The published ancestor was `5fac85c1db84f7edade02334538565ed655db4c5`.
Before consolidation, the local source corpus had the builder identity
`fc9c2b1f09f549c52d947a1903258ab5366d949e30b9ea9b8a7a4c0226a83536`.
These identities describe different source states. The selected consolidation
also adopts the already formed context method and aligns Windows device-name
handling with the generator, including console names, superscript COM/LPT
digits, DEL and spaces before a device extension.

The corpus is consolidated into an ordinary source commit before constructing
the release selection. The selection must name that actual commit, identify
the chosen method source files and retain the generated plan. A Git ancestor
alone is not the identity of uncommitted source content.

The source-only package built at this consolidation is a reproducibility and
compatibility result. Selecting the generated input as the default build is
the following source increment, distinct from publishing a numbered release,
changing a website or updating already installed projects.

## Selected generated input

The consolidation is `7c864c4220b7bc05584036ee3cea91058ec16f8e`; its normalized
builder source identity is `44f5d2eaf8a9d623beef3e7e1eb8d37e16ca60572c1293e7531f0e334e6d04ce`.
Every selected body was read from that commit, and the SourceManifest records
its actual source path and normalized content hash. The next source increment
adds the maintained generated selection and makes it the ordinary build default.
Its current builder tree therefore has its own identity, separate from the
corpus used to form the input. See [selection](../release/GENERATED_KERNEL_SELECTION.json).

The retained plan has canonical SHA-256
`84c96aebbd8043ba4239f78c3d21e270f4cbb6241dc75359b21ec32c363a26c1`.
The compiler source is `69524c315919dbc48dd92c4362e76196a239ac7e`, version
`0.4.0.dev5`. This selects the next release's generated input in ordinary source;
it does not rename the existing 3.2.0 tag or publish new release assets.
