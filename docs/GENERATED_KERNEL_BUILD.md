# Build from a generated kernel selection

The ordinary product build consumes the maintained selection in
[GENERATED_KERNEL_SELECTION.json](../release/GENERATED_KERNEL_SELECTION.json).
It retains the actual corpus commit, compiler revision and canonical plan hash.
Run `python tools/build_release.py` to build that selection. If the selection
is missing, ordinary building stops before replacing the package; it never
falls back to the source projection. No generator checkout
is required for this build; the exported result is part of the source repository.

To deliberately override it with another identified generation plan:

```powershell
python tools/build_release.py --kernel-plan /path/to/generation-plan.json --kernel-plan-sha256 CANONICAL_PLAN_SHA256 --package-dir /path/to/candidate
python tools/verify_distribution.py --package-dir /path/to/candidate
```

The hash is SHA-256 of UTF-8 JSON with sorted keys, no insignificant whitespace
(`separators=(",", ":")`) and literal Unicode (`ensure_ascii=False`). It identifies
the selected complete plan, not merely the producer's reported plan ID. Select it
from the generator's retained output and reasons. It is an integrity binding, not
a signature or an independent endorsement of the selected methods.

Production competences form the SourceManifest, ProjectModel and SeedSpec.
Its normal `plan` command produces the result consumed here. This builder does not
decide competence contents from a hidden template or invoke a language model. The
existing materialization record selects the artifact bodies and competence/resource
relations; unselected scaffold, generic entry and private source atlas stay outside
the product. The generator source is not required to build from an exported plan,
install the resulting package or run its local helpers.

## What the product owns

`generated_kernel.py` maps selected skill paths to `payload/skills/`, generic
resources to `payload/resources/`, and the autonomous kernel resource namespace
to `payload/.maios/kernel/`. The mapping preserves generic skill/resource layout;
autonomous methods are formed for the product's kernel paths. It does not rewrite
links in arbitrary generated text. A different location needs a deliberate product
binding and appropriate receiving-method formation.

When generation is selected, the builder replaces the source projection's skill
bodies and Markdown kernel resources with the materialized selection. It does not
silently restore an omitted old body. The product's actual entry/runtime contracts
still apply: omitting a required operating organ produces an invalid distribution.
This preserves the autonomous product's behavior without fixing the selection to
its historical file count. New skill names and nested resources can be delivered.

Product contracts, host adapters, installer, initial state and historical profile
translation remain product-owned. Generated content cannot overwrite these paths.
The project AGENTS entry reaches the selected competences while retaining the
project system competence as its operating owner. Generation does not add a second
generic kernel or preconfigure an unknown recipient's context.

`MANIFEST.json.generated_kernel` records the selected plan identity, compiler,
input identities and exact delivered artifact/resource paths and hashes. Source
tree identity describes the builder base separately. The inventory covers actual
distribution bytes. Verification checks generated bodies, resource presence and
entry reachability as well as the existing product contracts. These checks do not
establish model use, comprehension, assimilation or authenticity of the producer.

## Retained contract compatibility

This consumer supports `repokernel.generation-plan.v1` with
`repokernel.competence-materialization-record.v1`. The actual producer exercised
is `0.4.0.dev5`; compatibility is not inferred for arbitrary future schemas.
The plan must be unblocked and intended for a new repository. A distribution
selected here still supports installation into new and existing receiving projects
through the ordinary installer. Existing project conflict refusal and recovery
remain installer-owned. A retrofit plan for a particular repository is a different
input relation and is not repurposed as an autonomous distribution.

The compatibility source-only build is explicit: `python tools/build_release.py
--source-only`. The default is now the generated selection. An override must
supply both plan and canonical hash. Numbered release publication remains separate.

## Evolving the source

Public contributors can change native product sources and propose method changes
in a pull request. The ordinary build consumes the retained method selection:
editing a selected source body alone does not replace its exported counterpart.
Maintainers renew that selection through the [production method](RENEW_KERNEL_SELECTION.md).
That operation requires the private compiler and is separate from the public
build above. A contributor does not need access to it to study, test or propose
changes to this repository.

Use `--source-only` explicitly to inspect the native-source projection when
appropriate. It is a compatibility candidate, not an equivalent reconstruction
of the maintained generated distribution. Keep package disposition explicit.
