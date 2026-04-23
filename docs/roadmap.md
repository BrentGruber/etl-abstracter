# Roadmap

## Delivery strategy

The safest path is to build this in phases and avoid over-abstracting early.

The initial goal should not be to support every possible pipeline shape. The initial goal should be to prove that a declarative DSL, policy-based backend selection, secure connection resolution, and reliable orchestration can work end to end for a narrow but real slice of use cases.

The first implementation should be **open source backend first**:
- CDC lane: Debezium
- batch / sync lane: Airbyte

Enterprise vendor backends should come later:
- HVR
- Informatica

That lets the platform validate the control-plane model early, defer expensive vendor integration work, and later add support-tier policy logic for critical workloads.

## Phase 0: Architecture, contracts, and local sandbox

### Deliverables
- written architecture spec
- `Pipeline` v1 shape
- `Connection` v1 shape
- OSS-first backend capability matrix
- policy model
- canonical internal data model
- local docker-compose sandbox design
- Phase 0 checklist with example scenarios

### To do
- write a short v1 scope statement
- define explicit non-goals for v1
- choose initial OSS backends
  - Debezium for CDC
  - Airbyte for batch / sync
- define the `Pipeline` v1 resource boundary
- define the `Connection` v1 resource boundary
- define how `Pipeline` references `Connection`
- define what fields are forbidden in pipeline specs, especially credentials
- define minimal dataset/object reference conventions
- define minimal `Pipeline` v1 sections
- define minimal `Connection` v1 sections
- define the policy input contract
- define the initial plan object model
- define the lifecycle state model
- define the connection registry / resolver approach
- define the secrets-backed connection resolution flow
- build a capability matrix for Debezium and Airbyte
- define unsupported combinations that must be rejected in v1
- create canonical example specs
- design a local docker-compose stack for testing
  - include Debezium and Airbyte
  - include source and destination systems
  - include seeded source data
  - include recurring generated updates to source data

### Validation strategy
- architecture review
- model at least five representative example pipelines
- confirm each example can either map cleanly or fail clearly
- confirm the docker-compose sandbox is sufficient to exercise both CDC and batch flows

## Phase 1: DSL, validation, and example set

### Deliverables
- YAML parser
- JSON Schema validation
- semantic validation layer
- validation CLI
- sample specs
- initial `Connection` validation support

### To do
- write initial JSON Schema for `Pipeline`
- write initial JSON Schema for `Connection`
- implement parser in Go
- implement semantic checks
- implement connection reference validation
- create examples for:
  - CDC pipeline routed to Debezium
  - batch pipeline routed to Airbyte
  - invalid pipeline
  - connection policy violation
- produce readable validation errors

### Validation strategy
- unit tests for valid and invalid specs
- golden tests for sample files
- CLI output review for usability

## Phase 2: Policy engine

### Deliverables
- OPA integration
- initial Rego policy set
- decision explanation output

### To do
- define policy input JSON
- implement routing rules:
  - CDC -> Debezium
  - batch / sync -> Airbyte
- implement rejection rules for unsupported combinations
- implement approval rules for risky changes
- implement connection usage policy checks
- expose human-readable explanation output
- document future policy extension points for:
  - critical CDC -> HVR
  - critical batch -> Informatica

### Validation strategy
- table-driven policy tests
- snapshot tests for explanations
- CI output review to ensure decisions are understandable

## Phase 3: Planner and compiler

### Deliverables
- internal plan model
- Debezium compiler
- Airbyte compiler
- plan diff support

### To do
- define plan object model
- map abstract DSL to Debezium operations
- map abstract DSL to Airbyte operations
- classify create, update, delete, and no-op
- mark destructive or high-risk operations

### Validation strategy
- deterministic golden tests
- readable plan output review
- repeated input should generate identical plans

## Phase 4: Control plane API and state store

### Deliverables
- API service
- Postgres schema
- persistence for pipeline, connection, and execution state

### To do
- design tables for:
  - pipeline specs
  - connection metadata
  - selected backend
  - rendered plans
  - lifecycle state
  - workflow runs
  - observed backend state
- implement endpoints for:
  - validate
  - plan
  - apply
  - status

### Validation strategy
- API contract tests
- migration tests
- persistence and recovery tests

## Phase 5: Workflow orchestration and connection resolution

### Deliverables
- Temporal workflows
- backend activities
- lifecycle state integration
- connection resolution path

### To do
- implement workflows for:
  - validate and plan
  - apply
  - verify
  - delete
- implement retry policies
- implement compensation paths
- implement secrets-backed connection resolution for apply-time use
- map workflow progress to lifecycle states

### Validation strategy
- workflow unit tests
- retry and idempotency tests
- failure injection tests
- recovery tests after interrupted execution
- connection resolution integration tests

## Phase 6: Debezium adapter

### Deliverables
- Debezium integration for CDC pipelines

### To do
- implement auth handling
- implement connection/config translation
- implement create, update, read, and delete actions
- implement state read-back for verification
- normalize Debezium-specific errors

### Validation strategy
- mocked adapter tests
- sandbox integration tests
- create/update/no-op/delete coverage

## Phase 7: Airbyte adapter

### Deliverables
- Airbyte integration for batch / sync pipelines

### To do
- implement auth handling
- implement object translation
- implement create, update, read, and delete actions
- read back state for verification
- normalize Airbyte-specific errors

### Validation strategy
- mocked adapter tests
- sandbox integration tests
- create/update/no-op/delete coverage

## Phase 8: GitHub integration

### Deliverables
- pull request validation workflow
- plan preview comments
- apply on merge

### To do
- create GitHub Actions workflows for:
  - validation
  - policy evaluation
  - planning
  - apply trigger
- publish concise plan summaries into PRs
- surface approval requirements clearly

### Validation strategy
- PR happy-path test
- invalid spec test
- approval-gated change test
- merge-to-apply test

## Phase 9: Drift detection and observability

### Deliverables
- drift detection
- execution metrics
- traces and logs

### To do
- implement periodic reconcile jobs
- compare desired state and observed backend state
- mark pipelines as Drifted when needed
- instrument API, planner, workflows, and adapters
- publish operational dashboards if useful

### Validation strategy
- simulate manual backend drift
- verify detection and state transition
- confirm traces for full apply path

## Phase 10: Vendor backend expansion

### Deliverables
- HVR adapter
- Informatica adapter
- support-tier policy extension

### To do
- implement HVR integration for critical CDC pipelines
- implement Informatica integration for critical batch pipelines
- add policy logic for critical vs non-critical routing
- expand capability matrices to include vendor backends
- define migration or override logic for moving selected pipelines to vendor lanes

### Validation strategy
- mocked adapter tests
- sandbox or non-prod vendor integration tests
- critical workload routing policy tests
- plan compatibility review between OSS and vendor backends

## Phase 11: Production hardening

### Deliverables
- authn/authz
- audit trail
- approval model
- secrets hardening

### To do
- secure backend credentials
- implement least-privilege access patterns
- add audit records for changes and decisions
- require approvals for destructive changes
- isolate environments cleanly

### Validation strategy
- security review
- least-privilege review
- audit verification
- secrets handling review

## Suggested MVP checkpoint

A good MVP is complete when the system can do all of the following reliably:

1. accept a valid YAML `Pipeline` spec
2. validate referenced `Connection` resources
3. select Debezium for a CDC example
4. select Airbyte for a batch example
5. generate a readable backend-specific plan
6. apply that plan through Temporal
7. verify final state
8. report clear status and failure reasons

## Phase 0 checklist

### Product boundary
- [ ] write a short v1 scope statement
- [ ] define explicit non-goals for v1
- [ ] confirm initial OSS backend choices
  - [ ] Debezium
  - [ ] Airbyte

### Local sandbox
- [ ] design docker-compose stack for local testing
- [ ] include Debezium and Airbyte in the stack
- [ ] choose source systems for local testing
- [ ] choose destination systems for local testing
- [ ] include seeded source data
- [ ] include recurring generated source updates
- [ ] document how sandbox scenarios map to pipeline examples

### Resources and DSL
- [ ] define the `Pipeline` v1 resource boundary
- [ ] define the `Connection` v1 resource boundary
- [ ] define how `Pipeline` references `Connection`
- [ ] define minimal v1 sections for `Pipeline`
- [ ] define minimal v1 sections for `Connection`
- [ ] define forbidden fields in pipeline specs, especially credentials
- [ ] define dataset/object reference conventions

### Policy and planning
- [ ] define policy input shape
- [ ] define initial routing decision table
- [ ] define lifecycle states
- [ ] define plan object structure
- [ ] define unsupported combinations and rejection behavior

### Connections and security
- [ ] define connection registry approach
- [ ] define secrets-backed resolution flow
- [ ] define connection usage policy model
- [ ] define normalized resolved connection payload for adapters

### Examples and validation
- [ ] create canonical example specs
  - [ ] CDC example routed to Debezium
  - [ ] batch example routed to Airbyte
  - [ ] invalid example
  - [ ] connection policy violation example
  - [ ] unsupported capability example
- [ ] confirm each example can be routed or rejected clearly

## Initial implementation to-do list

### Foundations
- [ ] write an ADR for the control-plane approach
- [ ] define the DSL v1 field set
- [ ] define the `Connection` v1 field set
- [ ] create sample pipeline and connection specs
- [ ] build capability matrices for Debezium and Airbyte
- [ ] define the canonical internal model

### Validation and policy
- [ ] create JSON Schema
- [ ] build semantic validation rules
- [ ] define policy input shape
- [ ] write initial Rego policies
- [ ] implement explanation output

### Planning and execution
- [ ] define the internal plan model
- [ ] implement Debezium compiler
- [ ] implement Airbyte compiler
- [ ] bootstrap Go API service
- [ ] add Postgres-backed state persistence
- [ ] add Temporal workers

### Integrations
- [ ] implement Debezium adapter CRUD operations
- [ ] implement Airbyte adapter CRUD operations
- [ ] normalize backend errors into platform errors

### Delivery workflows
- [ ] build GitHub Action for validate and plan
- [ ] post plan summary to PRs
- [ ] add apply-on-merge workflow

### Reliability
- [ ] add idempotency protections
- [ ] add drift detection
- [ ] add metrics, tracing, and structured logs
- [ ] create failure playbooks
