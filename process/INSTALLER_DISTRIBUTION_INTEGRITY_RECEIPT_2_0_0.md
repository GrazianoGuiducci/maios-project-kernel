# Installer distribution integrity receipt — MAIOS Project Kernel 2.0.0

date: 2026-08-24
status: corrected and regression-verified; final archive identity owned by the external build receipt

## Entering failure

The candidate ZIP itself contained no compiled bytecode. Running the extracted
installer with ordinary Python nevertheless imported its embedded module and
created `payload/.maios/installer/__pycache__/installer.cpython-313.pyc`.
Because installation enumerated the live extracted `payload/` tree, that
undeclared host-generated file entered the preview and installed target.

This disproved the stronger claim that exact archive identity alone fixed the
installation input after extraction.

## Source correction

- the distribution entry sets `sys.dont_write_bytecode` before importing the
  embedded installer;
- the installer verifies the complete extracted distribution against
  `PACKAGE_INVENTORY.json` before it creates a plan;
- missing, changed, symlinked or untracked distribution files are refused;
- payload entries come only from the verified inventory, not a live directory
  enumeration;
- the distribution verifier explicitly forbids `__pycache__`, `.pyc` and
  `.pyo` artifacts.

## Regression proof

The fresh-process archive fixture now invokes the extracted installer without
Python `-B`, completes preview and apply, and observes no `__pycache__` in the
distribution. A counterexample fixture injects an untracked bytecode-shaped
file and verifies that planning fails before target mutation.

## Claim boundary

This receipt proves inventory-bound local installation input and bytecode
residue refusal. It does not prove semantic host use, provider behavior,
maintained reentry, publication or release.
