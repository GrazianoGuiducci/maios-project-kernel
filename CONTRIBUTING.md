# Contributing

Issues and focused proposals are welcome. Before proposing a change, identify:

- the user or project condition it addresses;
- the observable result that should improve;
- whether the change belongs to the public Project Kernel or to the private
  RepoKernel generator;
- the hosts and states affected;
- the evidence that would show an improvement without a regression.

Fork the repository, create a focused branch in your fork, and open a pull
request against the original `main` branch. Keep each proposal tied to one
observable project condition and result.

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
