# Deltas

Durable accepted changes for MAIOS Self-Configuring Project only.

## Minimum-Action Rule

Preserve a delta only when it changes the next action, prevents a repeated
error, clarifies a boundary, promotes or deprecates a source, or records a
reusable project method.

## Delta Receipt

```text
trigger:
source:
accepted_correction:
boundary:
expected_next_action_change:
validation:
status: proposed | accepted | superseded
```

Do not preserve ordinary chat, duplicate summaries, secrets, credentials,
private material for public surfaces or speculation that has not changed a
reviewed action.
