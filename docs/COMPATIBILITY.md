# Host entries

MAIOS Project Kernel uses one shared project structure with entry files and
guides for the supported coding environments.

| Environment | Entry | Guide | Open the project |
|---|---|---|---|
| ChatGPT Codex | `AGENTS.md` | `CODEX_SETUP.md` | Open the extracted folder in Codex |
| Claude Code | `CLAUDE.md` | `CLAUDE.md` | Open the extracted folder in Claude Code |
| OpenCode | `AGENTS.md` | `OPENCODE_SETUP.md` | Open the extracted folder in OpenCode |
| Hermes | `AGENTS.md` | `HERMES_SETUP.md` | Open the extracted folder in Hermes |
| DeepSeek Harness (DSH) | `AGENTS.md` | `DSH_SETUP.md` | Use the extracted folder as the DSH project root |

For DSH, the `standard` preset is the baseline. Portable project skills are in
`.agents/skills/`; the package does not select a provider or model and does not
change the global DSH configuration.

Codex can optionally install the project lifecycle files included under
`package/.repokernel/lifecycle/`. The Project Kernel works without that optional
installation.

The machine-readable host map is
[`package/HOST_ADAPTERS.json`](../package/HOST_ADAPTERS.json).
