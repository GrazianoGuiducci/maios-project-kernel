# Hermes native discovery receipt — MAIOS Project Kernel 2.0.0

date: 2026-08-24
status: verified for project-local native skill discovery only

## Entering failure

The declared `hermes` adapter had no projection and assumed that Hermes would
discover the canonical project `skills/` directory. Native Hermes 0.20.0 source
and offline behavior showed that it scans `HERMES_HOME/skills` plus explicitly
configured external directories. Adapter declaration and root instructions
therefore did not prove or enable native skill discovery.

## Source correction

- project the one canonical semantic owner to
  `.hermes/skills/maios-project-system/SKILL.md`;
- keep the project-local Hermes home additive and selected per process;
- install `.hermes/.gitignore` so host-created configuration, credentials,
  sessions and caches do not enter repository tracking;
- never copy or modify the user's global Hermes profile;
- make distribution verification reject every non-generic adapter that does
  not project the one semantic owner exactly once.

## Observation

An archive generated from the corrected living source was installed into an
absent target with `--host hermes`. With `HERMES_HOME` set to the installed
project `.hermes` directory:

```text
hermes skills list --source local
-> maios-project-system | local | local | enabled
-> 0 builtin, 1 local, 1 enabled

hermes prompt-size --platform cli --json
-> one skills_breakdown entry at the adapter-installed path
-> SKILL.md bytes: 3961
-> memory bytes: 0
-> user profile bytes: 0
-> API calls: 0
```

The installed skill SHA-256 was
`e33018b4b51edaada4e21afc8aed22a207ba9d5c54381e138b0b24b168bbc3e6`.
The project-local host attestation advanced only `skill_discovery` to
`verified`; `state_read`, `behavioral_activation` and `maintained_reentry`
remain `unverified`.

## Provider boundary

The isolated Hermes home had no model, key, OAuth credential or prior session.
No provider call was attempted and no global profile or credential was copied.
Semantic use requires a later explicit credential binding to this isolated
proof surface or another independently fresh supported host.

## Claim boundary

This receipt proves the corrected adapter path, exact installed skill bytes and
Hermes-native offline discovery. It does not prove that a model read project
state, exercised the kernel, improved a result or reentered in a later session.
The final corrected archive identity is owned by `dist/BUILD_RECEIPT.json` after
the last deterministic rebuild.
