# Provenance and reproducibility

## Source owner

Version 2.0.0 is built from this `maios-project-kernel` repository. The package
does not import a prepared payload from `maios_it`, MAIOS Form state, private
RepoKernel source, D-ND/TMx topology, credentials, runtime state, or lifecycle
hooks. Historical 1.6 files and the separate cut-down 2.0 attempt are comparison
evidence only.

The maintained source positions and exclusions are declared in
[`sources/SOURCE_MANIFEST.json`](../sources/SOURCE_MANIFEST.json). The exact
source-to-distribution mapping is
[`release/PROJECTION.json`](../release/PROJECTION.json).

## Content identity

The builder records:

- SHA-256 of every decision-relevant source-tree file outside generated output;
- SHA-256 of the projection and source manifest;
- exact package member paths, byte lengths, and SHA-256 values;
- deterministic ZIP SHA-256;
- a build receipt with distribution verification.

ZIP member order, timestamps, compression, and Unix file modes are fixed.
Two builds from the same source tree must be byte-identical.

## Claim boundary

A content-addressed source and reproducible archive prove artifact identity.
They do not prove installation, native host discovery, semantic use, external
effects, useful behavior, maintained reentry, or human acceptance. Those states
must point to their own receipts or observations.
