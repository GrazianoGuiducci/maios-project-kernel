# Host compatibility

Version `1.3.0` uses one shared Project Kernel and host-native entry files.

| Host | Included entry | Included guide | Initial claim |
|---|---|---|---|
| ChatGPT Codex | `AGENTS.md` | `CODEX_SETUP.md` | packaged; activation requires opening and evidence |
| Claude Code | `CLAUDE.md` | `CLAUDE.md` | packaged; activation requires opening and evidence |
| OpenCode | `AGENTS.md` | `OPENCODE_SETUP.md` | packaged; activation requires opening and evidence |
| Hermes | `AGENTS.md` | `HERMES_SETUP.md` | packaged; activation requires opening and evidence |

The authoritative machine-readable map is
`package/HOST_ADAPTERS.json`. Initial receipts under
`package/receipts/host-activation/` deliberately begin without claiming that a
host has loaded or exercised a capability.

Host products can change their discovery rules. Compatibility therefore means
that a supported entry and guide exist; it does not mean that every current or
future host version has been behaviorally verified.
