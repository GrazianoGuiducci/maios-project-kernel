# MAIOS Project Kernel

[Versione italiana](README.it.md)

MAIOS Project Kernel is a self-configuring package for starting a new project
with an AI assistant. You do not need to define the architecture, select the
skills, or even know the product in advance: it starts from the person's real
work, makes its understanding explicit, and proposes a first correctable
result.

The package gives the project an operational identity, working memory, sources,
capabilities, success criteria, and continuity. The person remains in control
of decisions; installations, publications, and external integrations are not
activated implicitly.

## Download and start

The recommended path is the
[Releases](https://github.com/GrazianoGuiducci/maios-project-kernel/releases/latest)
page, which provides the installable ZIP and its SHA-256 checksum.

1. Create a new, empty folder for the project.
2. Extract the entire ZIP into that folder.
3. Open the folder with your assistant.
4. Write: `Read START_HERE.md and let's begin the configuration.`

This release is designed for **a new project**. Do not extract it over an
existing repository; that case requires a separate integration path.

The installable source can be inspected in [`package/`](package/). The current
startup guide is in Italian at [`package/START_HERE.md`](package/START_HERE.md).

## Two entry paths, one function

MAIOS provides two ways to obtain a situated Project Kernel:

- **Self-configuring package:** context is discovered after download through an
  initial conversation with the person.
- **[MAIOS Form](https://maios.it/form.html):** starts from information that is
  already structured, then discusses and refines it before generation.

The first path can help a person who does not yet know what is possible in
their domain. The second starts from a more defined context. Both aim to create
an operational structure owned by the project, able to guide the work and
evolve without losing the reasons behind decisions.

## What is included

- a generated Project Kernel ready to be specified in its real context;
- a startup interview that turns problems, activities, and possibilities into
  a first correctable direction;
- configuration state, project brief, and re-entry point;
- a meta-faculty that selects and composes relevant capabilities;
- an evolution contract that distinguishes case memory, competence, skill,
  function, and meta-evolution;
- entries and guides for Codex, Claude Code, OpenCode, Hermes, and DeepSeek
  Harness (DSH);
- an optional, conflict-aware Codex lifecycle projection, packaged but not
  installed or activated.

Host-specific entry points are summarized in
[`docs/COMPATIBILITY.md`](docs/COMPATIBILITY.md).

## Recent evolution

Version `1.5.0` adds a host-native DSH projection: the extracted folder is the
DSH project root, `AGENTS.md` is the entry, and portable skills remain under
`.agents/skills/`. No DSH plugin, provider, model, hook, or global configuration
is required. The optional Codex lifecycle projection introduced in `1.4.0`
remains independently opt-in.

See [`CHANGELOG.md`](CHANGELOG.md) for the version history.

## Current status

- Package version: `1.5.0`
- Optional Codex lifecycle projection: packaged, not installed
- Mode: deferred configuration through a startup interview
- Target: new folder / new repository
- Existing-repository installation: not supported in this release

## Related repositories

- [`d-nd-seed`](https://github.com/GrazianoGuiducci/d-nd-seed) provides the
  public capability and faculty registries used as pinned, `data_only`
  generation references.
- [`d-nd-ux-ai-seed`](https://github.com/GrazianoGuiducci/d-nd-ux-ai-seed)
  contains public UX behavior contracts for agentic workspaces; it is a related
  ecosystem surface, not code bundled in this package.

The role and terms of the included sources are detailed in
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) and
[`docs/PROVENANCE.md`](docs/PROVENANCE.md).

## License

Repository content, excluding names and trademarks, is available under the
[MIT License](LICENSE). Informational sources and their terms are listed in
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md), while
names and marks are addressed in [`TRADEMARKS.md`](TRADEMARKS.md).
