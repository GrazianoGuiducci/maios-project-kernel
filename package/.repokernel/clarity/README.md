# Clarity Cleanup

Operational clarity ledger for MAIOS Self-Configuring Project.

Use this area to classify dirty, unclear, stale, duplicate or unowned
project files before any cleanup action.

## Classification

```text
path:
observed_state: dirty | untracked | generated | stale | duplicate | unknown
owner: current-agent | operator | generated-tool | external | unknown
risk: safe | review_required | sensitive | destructive
proposed_action: keep | commit | document | archive | ignore | delete_candidate | ask_owner
evidence:
gate:
receipt:
```

## Boundary

This ledger does not authorize deletion, moving files, changing ignore rules,
normalizing line endings in bulk or rewriting history. It only makes the
cleanup decision inspectable.
