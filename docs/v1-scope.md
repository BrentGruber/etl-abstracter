# v1 Scope

## Goal

The first version of this project should prove that a declarative, policy-driven data control plane can:
- accept pipeline intent as code
- validate it
- select an appropriate open source backend
- compile a plan
- apply that plan reliably
- verify the resulting state

This version should optimize for learning and fast iteration, not enterprise completeness.

## OSS-first implementation strategy

The first implementation should start purely with open source backends for testing and development.

Initial backend targets:
- **Debezium** for CDC-oriented pipelines
- **Airbyte** for batch / sync-oriented pipelines

Vendor-supported backends should come later:
- HVR
- Informatica

The long-term policy model can eventually support rules such as:
- critical CDC pipelines -> HVR
- critical batch pipelines -> Informatica
- non-critical CDC pipelines -> Debezium
- non-critical batch pipelines -> Airbyte

But that vendor-tier policy is explicitly **not** part of initial implementation.

## In scope for v1

### Core resources
- `Pipeline`
- `Connection`

### Core capabilities
- declarative pipeline specs in YAML
- connection references via `connectionRef`
- connection metadata separated from secret material
- validation of schema and semantics
- policy-driven backend routing
- plan generation
- apply and verify workflows
- lifecycle state tracking
- readable failure and decision explanations

### Initial backend lanes
- CDC lane using Debezium
- batch / sync lane using Airbyte

### Core platform pieces
- Go-based parser / planner / API
- OPA for policy evaluation
- Temporal for orchestration
- Postgres for state and connection metadata
- GitHub and GitHub Actions for workflow entrypoints

## Explicitly out of scope for v1

- HVR adapter implementation
- Informatica adapter implementation
- vendor-support policy tiers
- rich transformation language
- full semantic layer implementation
- report-as-code implementation
- rich UI
- large plugin ecosystem
- broad multi-tenant enterprise governance model
- exhaustive lineage platform

## Phase 0 priority: local sandbox stack

One of the first pieces of Phase 0 should be a local docker-compose test environment that gives the project a repeatable playground.

### Required characteristics
The stack should include:
- open source backend tools
  - Debezium
  - Airbyte
- at least one source data system
- at least one destination data system
- seeded initial source data
- recurring generated source updates to simulate change over time

### Good candidate local stack
A very reasonable first stack could include:
- PostgreSQL source
- Debezium + Kafka + Kafka Connect
- Airbyte
- PostgreSQL destination
- optional MinIO or object-store destination later
- a small data generator / seeder service

### Purpose of the sandbox
This environment should let the team:
- validate backend assumptions quickly
- test pipeline behavior repeatedly
- exercise CDC and batch paths locally
- refine the DSL against real system behavior
- reduce ambiguity before deeper implementation

## Minimal `Pipeline` v1 direction

The first implementation should focus on a reduced pipeline spec.

Good v1 sections:
- `ownership`
- `sources`
- `targets`
- `semantics`
- `execution`
- `delivery`
- `governance`
- `backendHints`

Deferred or heavily constrained in v1:
- advanced `transform`
- deep `quality`
- rich `observability`
- complex multi-stage graph execution

## Minimal `Connection` v1 direction

A `Connection` resource should represent:
- connection type
- environment
- endpoint metadata
- auth secret reference
- governance restrictions
- capability hints

The actual credentials should live in a secrets manager or secret-backed resolution path, not in pipeline specs.

## Success criteria for v1

The first version is successful if it can reliably:
1. validate a pipeline spec and referenced connections
2. route a CDC example to Debezium
3. route a batch example to Airbyte
4. reject unsupported examples with a clear explanation
5. generate a readable plan
6. apply that plan using Temporal workflows
7. verify the observed result
8. surface state and failure information clearly

## Guiding principle for v1

Keep the first release narrow and trustworthy.

The system does not need to prove every long-term idea immediately. It needs to prove that declarative intent, policy-driven backend selection, secure connection resolution, and reliable execution can work together in a clean control-plane model.
