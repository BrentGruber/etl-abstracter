# Roadmap

## Delivery strategy

The safest path is to build this in phases and avoid over-abstracting early.

The initial goal should not be to support every possible pipeline shape. The initial goal should be to prove that a declarative DSL, policy-based backend selection, and reliable orchestration can work end to end for a narrow but real slice of use cases.

## Phase 0: Architecture and contracts

### Deliverables
- written architecture spec
- DSL v1 shape
- backend capability matrix
- policy model
- canonical internal data model

### To do
- define the `Pipeline` resource shape
- define required metadata and ownership fields
- define source and target model
- define semantics model
- define policy input contract
- define state persistence model
- define HVR capability matrix
- define Informatica capability matrix

### Validation strategy
- architecture review
- model at least five representative example pipelines
- confirm each example can either map cleanly or fail clearly

## Phase 1: DSL and validation

### Deliverables
- YAML parser
- JSON Schema validation
- semantic validation layer
- validation CLI
- sample specs

### To do
- write initial JSON Schema
- implement parser in Go
- implement semantic checks
- create examples for:
  - CDC pipeline
  - batch pipeline
  - invalid pipeline
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
  - CDC -> HVR
  - batch -> Informatica
- implement rejection rules for unsupported combinations
- implement approval rules for risky changes
- expose human-readable explanation output

### Validation strategy
- table-driven policy tests
- snapshot tests for explanations
- CI output review to ensure decisions are understandable

## Phase 3: Planner and compiler

### Deliverables
- internal plan model
- HVR compiler
- Informatica compiler
- plan diff support

### To do
- define plan object model
- map abstract DSL to HVR operations
- map abstract DSL to Informatica operations
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
- persistence for pipeline and execution state

### To do
- design tables for:
  - pipeline specs
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

## Phase 5: Workflow orchestration

### Deliverables
- Temporal workflows
- backend activities
- lifecycle state integration

### To do
- implement workflows for:
  - validate and plan
  - apply
  - verify
  - delete
- implement retry policies
- implement compensation paths
- map workflow progress to lifecycle states

### Validation strategy
- workflow unit tests
- retry and idempotency tests
- failure injection tests
- recovery tests after interrupted execution

## Phase 6: HVR adapter

### Deliverables
- HVR integration for CDC pipelines

### To do
- implement auth handling
- implement connection/config translation
- implement create, update, read, and delete actions
- implement state read-back for verification
- normalize HVR-specific errors

### Validation strategy
- mocked adapter tests
- sandbox integration tests
- create/update/no-op/delete coverage

## Phase 7: Informatica adapter

### Deliverables
- Informatica integration for batch pipelines

### To do
- implement auth handling
- implement object translation
- implement create, update, read, and delete actions
- read back state for verification
- normalize Informatica-specific errors

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

## Phase 10: Production hardening

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

1. accept a valid YAML pipeline spec
2. select HVR for a CDC example
3. select Informatica for a batch example
4. generate a readable backend-specific plan
5. apply that plan through Temporal
6. verify final state
7. report clear status and failure reasons

## Initial implementation to-do list

### Foundations
- [ ] write an ADR for the control-plane approach
- [ ] define the DSL v1 field set
- [ ] create sample pipeline specs
- [ ] build capability matrices for HVR and Informatica
- [ ] define the canonical internal model

### Validation and policy
- [ ] create JSON Schema
- [ ] build semantic validation rules
- [ ] define policy input shape
- [ ] write initial Rego policies
- [ ] implement explanation output

### Planning and execution
- [ ] define the internal plan model
- [ ] implement HVR compiler
- [ ] implement Informatica compiler
- [ ] bootstrap Go API service
- [ ] add Postgres-backed state persistence
- [ ] add Temporal workers

### Integrations
- [ ] implement HVR adapter CRUD operations
- [ ] implement Informatica adapter CRUD operations
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
