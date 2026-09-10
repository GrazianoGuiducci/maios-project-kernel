# Contributing

Issues, focused proposals, and competence contributions from people or capable
AI models are welcome. Before proposing a change, identify:

- the user or project condition it addresses;
- the observable result that should improve;
- which public Project Kernel source owns the change;
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
state `no_change`, `candidate`, or `selected` for package disposition. The
source projection in `release/PROJECTION.json` and the retained generated
selection determine what is delivered. Change the appropriate source owner;
never hand-edit `package/`.

For method bodies supplied by the retained selection, editing the public native
source does not replace the exported body consumed by the ordinary build.
Maintainers renew that selection through the [production renewal method](docs/RENEW_KERNEL_SELECTION.md).
You can study, edit, test and propose public source changes without the private
compiler. The [build guide](docs/GENERATED_KERNEL_BUILD.md) explains which source
changes the ordinary build consumes and when an explicit source-only candidate
is useful for checking a native method change.

Contributions should preserve the distinction between a file being included,
discovered, configured, and actually active.

Run the local validation before opening a pull request:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B -m unittest discover -s tests -v
python -B tools/build_release.py
python -B tools/verify_distribution.py
```

By submitting a contribution, you agree that it may be distributed under the
MIT License of this repository.
