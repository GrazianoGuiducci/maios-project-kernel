# Project Operations

Operating context and material-action receipts for MAIOS Self-Configuring Project.

## Operating Context

Resolve these fields before mutation. They are independent.

```text
acting_context:
state_provider:
active_surface:
write_owner:
runtime_boundary:
current_evidence:
residue_not_to_follow:
```

Visibility of state does not activate a workstream or grant write authority.

## Material Action Receipt

```text
intent:
surface:
owner:
side_effect_class: local_only | source_remote | production_bound | external
source_verified:
gate:
validation:
side_effects:
recovery:
next_legal_action:
```

Do not repeat material effects from a transcript, packet or stale plan alone.

## Routine Candidate

```text
repeated_signal:
trigger:
inputs:
outputs:
owner:
gate:
validation:
stop_condition:
status: observed | candidate | accepted | superseded
```

This ledger proposes operating context and routines. It does not install hooks,
schedule work, clone node state or increase project authority.
