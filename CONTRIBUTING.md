# Contributing

Issues, focused proposals, and competence contributions from people or capable
AI models are welcome. Before proposing a change, identify:

- the user or project condition it addresses;
- the observable result that should improve;
- whether the change belongs to the public Project Kernel or to the private
  RepoKernel generator;
- the hosts and states affected;
- the evidence that would show an improvement without a regression.

Fork the repository, create a focused branch in your fork, and open a pull
request against the original `main` branch. Keep each proposal tied to one
observable project condition and result.

## Contribute a competence

Read [`contributions/README.md`](contributions/README.md) and use the
[`Competence Contribution template`](contributions/COMPETENCE_CONTRIBUTION_TEMPLATE.md).
A contribution can be a competence, method, source correction, evidence item,
falsifier, research delta, test, or implementation patch. Choose the smallest
owner-native form able to carry the reusable difference.

The contribution should preserve:

- its source relation and claim state;
- the present need or possibility;
- the closest public owner;
- the expected or observed resultant;
- causal readback, invalidator, and reentry condition;
- affected surfaces and explicit no-change surfaces.

KA keeps the possibility field open, FDLA preserves causal coherence while the
contribution is formed, and Meta_Skill composes or evolves the competence that
can continue the reusable difference. This is the canonical relation for every
contributor; identity does not grant truth or effect authority.

## AI-assisted contributions

Name the model and the exact public revision or uploaded source bundle it could
inspect. Separate repository facts, model inference, hypotheses, and proposed
form. Do not submit chat residue, private paths, credentials, personal data, or
hidden runtime state. The first GPT Pro packet is available at
[`contributions/GPT_PRO_START.md`](contributions/GPT_PRO_START.md).

## Package disposition

Public knowledge, research, and contribution competences are repository-native
and are not mapped into the current installable package. A pull request must
state `no_change`, `candidate`, or `selected` for package disposition. Only a
deliberate `release/PROJECTION.json` change selects package inclusion; never
hand-edit `package/`.

Do not submit credentials, private project material, personal data, or source
from RepoKernel. Contributions should preserve the distinction between a file
being included, discovered, configured, and actually active.

Run the local validation before opening a pull request:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B -m unittest discover -s tests -v
python -B tools/build_release.py
python -B tools/verify_distribution.py
```

By submitting a contribution, you agree that it may be distributed under the
MIT License of this repository.
