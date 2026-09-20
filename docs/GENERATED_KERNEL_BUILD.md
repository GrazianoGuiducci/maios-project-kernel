# Build from current product sources

The normal build reads the living owners declared in
[PROJECTION.json](../release/PROJECTION.json), the current family and autonomous
entry contracts, templates, adapters, installer and runtime. A public checkout
and Python 3.10 or later are sufficient. No private compiler, generated plan or
historical selection chooses the delivered method bodies.

```powershell
python -B tools/build_release.py
python -B tools/verify_distribution.py
python -B -m unittest discover -s tests -v
```

Edit the source owner, then rebuild `package/`; never edit its projection by
hand. Normal verification compares projected consumer bytes with those owners.
`PROJECT_ENTITY_PROFILE.json` derives its available competences from the mapping,
its policy from `AUTONOMOUS_ENTRY_CONTRACT.json` and its current catalogue hash
from the normalized bytes of `FACULTY_FIELD.json`. The manifest records current
product provenance. Historical compiler and seed identities remain historical
records under `release/`, outside the installed runtime.

Portable competences come from `adapters/ADAPTERS.json`. Each declared portable
owner must exist and have exactly one Codex discovery entry; the installed entry
points to its living body. Availability and discovery do not prove assimilation.

## Reproducibility and failure recovery

The source identity covers repository files except `.git`, `package`, Python/test
caches and top-level `.package.*` build directories. Text is normalized to LF;
binary bytes retain their identity. Use the default package location or an output
outside the source tree. Two builds from unchanged source must produce identical
member bytes, manifest and inventory.

Paths use one product-owned portable contract: no reserved Windows components,
trailing dots/spaces, control characters, case-fold aliases or file/parent
collisions. Both projection and installer validate it before an effect.

Each invocation acquires a unique staging directory. Rendering and verification
finish before promotion; the previous target is compared with its pre-build
identity. Promotion uses an exclusively acquired backup holder and restores the
old tree if replacement fails. Cleanup requires the same directory identity and
sealed contents. Foreign fixed names, concurrent changes and uncertain recovery
material remain untouched. An interrupted renderer can leave its unsealed unique
staging for qualified inspection; absence of automatic cleanup is deliberate.
This is caught-failure recovery, not arbitrary-writer serialization or a
multi-file crash-safe transaction.

## Explicit generated-plan compatibility

The retained `generated_kernel.py` consumer still accepts an identified,
unblocked `repokernel.generation-plan.v1` and its
`repokernel.competence-materialization-record.v1`. Select it explicitly:

```powershell
python -B tools/build_release.py --kernel-plan /path/to/plan.json --kernel-plan-sha256 CANONICAL_PLAN_SHA256 --package-dir /path/to/candidate
python -B tools/verify_distribution.py --package-dir /path/to/candidate
```

The expected hash is SHA-256 of canonical UTF-8 JSON with sorted keys,
`separators=(",", ":")` and `ensure_ascii=False`. It binds the complete selected
plan, not an endorsement of its producer. Explicit generation replaces selected
semantic projection bodies without silently restoring omitted owners; current
product contracts still apply. The manifest's optional `generated_kernel` records
only this explicitly exercised mode. `--source-only` remains a compatibility
alias for the normal direct build. Old retained selections are not read by default.

[Selection renewal](RENEW_KERNEL_SELECTION.md) remains an optional historical
producer workflow, not a public contribution or release prerequisite.

## Release candidate

After final source and documentation changes, build and verify again, then use:

```powershell
python -B tools/archive_candidate.py --output-dir /outside/source/candidate
```

This prepares a deterministic ZIP and SHA-256 file without a tag or Release.
CI uploads the same candidate archive from its checked commit. Source, package,
archive, CI and any later release retain separate exact identities. Publication
requires the selected final release review; package tests do not establish a
receiving model's semantic understanding or maintained behavioral assimilation.
