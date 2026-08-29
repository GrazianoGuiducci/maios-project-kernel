# Contribute competence

This repository accepts contributions from people and capable AI models as one
public competence field. A contribution is valuable when it preserves its
source relation, changes an attainable result or makes a testable possibility
available, and leaves the competence able to continue differently.

## Canonical law of contribution

```text
KA:
  the contributor's current representation does not close the possibility
  field around itself.

FDLA:
  source, object, meaning, status and result stay coupled; a detected
  deformation changes the contribution before it is projected.

Meta_Skill:
  existing competences compose first; a real reusable difference forms or
  evolves the smallest competence able to carry it.
```

This law applies equally to human, GPT Pro, Codex and other model
contributions. The author supplies provenance, not truth by identity.

## What can enter

- a new or evolved repository competence;
- a source-bound method or reference that changes later work;
- a test, counterexample, falsifier or competing explanation;
- a correction to Kernel knowledge or architecture;
- a paper or research delta with explicit claim state;
- a tool or implementation change supported by the owner source and tests.

A contribution does not need to become a `SKILL.md`. Choose the smallest form
that carries the reusable difference.

## Contribution body

Start from
[`COMPETENCE_CONTRIBUTION_TEMPLATE.md`](COMPETENCE_CONTRIBUTION_TEMPLATE.md)
and keep these relations visible:

```text
source relation
present need or possibility
closest public owner
competence or method body
expected or observed resultant
causal readback
invalidator
reentry condition
affected and unchanged surfaces
```

For code or architecture, include patch-ready paths and relevant tests. For a
paper or knowledge contribution, distinguish operator formulation,
hypothesis, represented relation, implementation evidence, observation and
retained unknown.

## AI-assisted contributions

State which model participated, what exact public revision or uploaded files
it could see, and which parts are its inference or proposed form. Remove chat
history, private paths, credentials, personal data and unrelated local state.

An AI return is contextual cognition. The portable part enters the closest
public owner; conversation residue stays outside. Use
[`GPT_PRO_START.md`](GPT_PRO_START.md) for the first GPT Pro cycle.

## Repository and package boundary

The public knowledge, research and contribution competences are
repository-native. They help a coder understand and evolve the clone, and are
not currently mapped into the installable `package/`.

```text
contribution available in repository
!= merged into main
!= selected for package projection
!= released
!= installed or discovered by a host
!= exercised or assimilated.
```

If real use later makes package inclusion material, change
`release/PROJECTION.json` deliberately and validate that product effect. Do not
hand-edit `package/`.

## Submission

1. Fork the repository and create a focused branch.
2. Add the contribution body and the smallest owner-native change.
3. Run the validation required by the changed surface.
4. Open a pull request that names the resultant, evidence, invalidator and
   package disposition.

Repository merge, package generation, release, installation and publication
remain separate effects. The maintainers integrate the contribution through
the same source and causal relation described above.
