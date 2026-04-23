# Phase 0 Sandbox Notes

## Why this stack exists

The local sandbox supports the earliest control-plane design work by giving the project a real environment where the future DSL and policy model can be tested against actual systems.

## Design choices in this first pass

### Source system
`postgres-source` is used because it is simple to run locally and supports CDC-oriented experimentation.

### Destination system
`postgres-destination` is used because it gives a straightforward sink for early sync and replication tests.

### CDC lane
Debezium is represented through:
- Kafka Connect using the Debezium image
- Kafka
- Kafka UI for visibility

### Batch / sync lane
Airbyte is included as the first open source batch / sync backend.

### Generated updates
A small Python generator creates recurring source changes so the environment is never static.

## Expected Phase 0 outcomes

This sandbox should help answer questions like:
- what minimal connection metadata is actually needed?
- what does a realistic source object reference look like?
- what do Debezium and Airbyte require from a compiled plan?
- where do unsupported combinations surface in practice?
- what should be modeled in the DSL versus hidden in backend adapters?

## Known limitations of this first draft

- Airbyte is present but not yet bootstrapped automatically
- Debezium is present but no connector is auto-created yet
- no object storage destination yet
- no orchestration or test harness scripts yet
- not production hardened

## Good follow-up tasks

- add connector bootstrap scripts
- add data reset scripts
- add end-to-end test scenarios
- add example pipeline specs tied to the sandbox
- decide whether MinIO should be added as another destination
