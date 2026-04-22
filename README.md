# ETL Abstracter

A GitOps-native control plane for declarative data movement.

## Vision

Build an enterprise system that completely abstracts ETL tooling behind a YAML-based DSL. Users define pipelines as code, and the platform determines the appropriate execution backend based on policy.

Initial backend routing examples:
- if change data capture is needed, use HVR
- if batch processing is needed, use Informatica

## Recommended framing

Rather than treating this as only an ETL abstraction layer, the stronger framing is:

- declarative data pipeline control plane
- policy-driven data integration orchestrator

This better reflects the reality that HVR and Informatica have different strengths and should be selected intentionally.

## Proposed tech stack

- GitHub
- GitHub Actions
- Temporal
- OPA
- Go
- Postgres
- JSON Schema
- OpenTelemetry (recommended)

## Guiding principles

1. Git is the source of truth
   - pipeline definitions live in Git
   - promotion happens through Git workflows
   - every decision is traceable to commits

2. Separate intent from implementation
   - users declare desired outcomes
   - the platform chooses the backend and implementation strategy

3. Policy decides placement
   - backend selection should live in OPA policy, not hardcoded logic

4. Support a common core plus backend-specific extensions
   - avoid over-abstracting real backend differences

5. Use an explicit compilation pipeline
   - parse
   - validate
   - enrich
   - evaluate policy
   - compile
   - plan
   - apply
   - verify

6. Require human review for impactful changes
   - destructive changes
   - topology changes
   - credential changes
   - high-risk backend transitions

7. Make orchestration idempotent and resumable
   - use Temporal for retries, waits, polling, and compensation

8. Build observability in from day one
   - execution history
   - policy decision trace
   - rendered plan
   - audit trail
   - drift detection

## Product concept

A policy-driven control plane for data movement where users declare pipelines in YAML and the platform compiles and deploys them into tools like HVR and Informatica.

## High-level architecture

### Layers

1. DSL / Spec layer
   - YAML authored by users
   - versioned schema
   - desired state declaration

2. Validation and enrichment
   - schema validation
   - semantic validation
   - defaults
   - reference checks

3. Policy engine
   - backend eligibility
   - compliance constraints
   - approval requirements
   - naming and ownership rules

4. Compiler / planner
   - maps abstract spec into backend-specific plans
   - detects create, update, delete, or no-op

5. Workflow orchestration
   - Temporal executes long-running backend workflows

6. Backend adapters
   - HVR adapter
   - Informatica adapter

7. Control plane API and state store
   - stores pipeline state
   - execution history
   - observed backend state

8. GitOps / CI integration
   - GitHub PR validation
   - plan preview
   - apply on merge

## Where each technology fits

### GitHub
- source of truth for pipeline specs
- pull request review
- promotion workflow
- audit trail

### GitHub Actions
- run validation
- run policy checks
- generate plan previews
- trigger apply workflows
- report status back to pull requests

### Temporal
- execute long-running workflows
- handle retries
- poll external systems
- support compensation and resumability

### OPA
- choose backend
- enforce policy
- explain selection decisions
- control approval requirements

### Go
- implement parser, validators, compiler, API, workers, adapters

### Postgres
- store control-plane state, execution history, and plan metadata

### JSON Schema
- structural validation for the YAML DSL

### OpenTelemetry
- traces, metrics, and observability for workflow execution

## Proposed DSL approach

Start with a common core and optional backend-specific extensions.

### Example DSL

```yaml
apiVersion: platform.data/v1alpha1
kind: Pipeline
metadata:
  name: customer-erp-to-warehouse
  owner: data-platform
  tags:
    domain: customer
    pii: high

spec:
  source:
    system: erp-prod
    type: oracle
    schema: customer
    table: customers

  target:
    system: snowflake-prod
    type: snowflake
    database: analytics
    schema: raw
    table: customers

  semantics:
    mode: cdc
    latencySla: near-real-time

  transform:
    type: passthrough

  requirements:
    historyRetentionDays: 30
    encryptionRequired: true
    dataResidency: us
    deletePropagation: true

  policyHints:
    preferredBackend: auto

backendExtensions:
  hvr:
    integrateMethod: log-based
```

## Initial policy examples

- if `semantics.mode == cdc`, prefer HVR
- if `semantics.mode == batch`, prefer Informatica
- if selected backend does not support the source or target, reject
- if compliance constraints are not met, reject
- if pipeline shape is supported only with approval, require approval

## Proposed state machine

### States
- Draft
- Validating
- PolicyEvaluating
- Planned
- AwaitingApproval
- Provisioning
- Verifying
- Active
- Drifted
- Updating
- Failed
- Deleting
- Deleted

### Typical lifecycle
- Draft
- Validating
- PolicyEvaluating
- Planned
- AwaitingApproval (optional)
- Provisioning
- Verifying
- Active

### Ongoing transitions
- Active -> Updating
- Updating -> Provisioning
- Active -> Drifted
- Active -> Deleting -> Deleted
- Provisioning -> Failed
- Verifying -> Failed

## Proposed user workflows

### 1. Create a new pipeline
1. author YAML spec in Git
2. open pull request
3. GitHub Actions run validation, policy evaluation, and planning
4. PR shows selected backend, policy explanation, and risk summary
5. reviewer approves
6. merge triggers apply
7. Temporal provisions resources
8. verification runs
9. status is published back to GitHub

### 2. Update an existing pipeline
1. modify YAML
2. CI produces plan diff
3. risky changes require approval
4. merge triggers update workflow
5. verification confirms health

### 3. Drift detection
1. reconcile worker compares desired state to backend state
2. mark pipeline as Drifted
3. alert or auto-reconcile depending on policy

### 4. Delete a pipeline
1. remove or disable YAML definition
2. plan shows deletion impact
3. approval if required
4. Temporal deprovisions resources
5. pipeline moves to Deleted

## Suggested system components

1. Spec parser and validator
2. Policy service
3. Planner / compiler
4. Control plane API
5. Temporal workflows and workers
6. HVR adapter
7. Informatica adapter
8. Drift detection and reconciliation worker

## MVP recommendation

Start with a narrow MVP:
- one DSL kind: `Pipeline`
- two backends: HVR and Informatica
- one routing rule set:
  - CDC -> HVR
  - batch -> Informatica
- GitHub PR workflow
- plan preview
- Temporal apply workflow
- status tracking
- no rich UI yet

### Explicitly exclude from MVP
- advanced transformation authoring
- broad self-service UI
- many backends
- complex multi-tenant governance
- marketplace-style plugins

## Biggest risks

1. Over-abstracting backend differences
2. Capability mismatch between DSL and backend reality
3. Poor visibility into why decisions were made
4. Assuming synchronous provisioning when backends are long-running
5. Ignoring drift between desired and actual state

## Step-by-step roadmap

### Phase 0: Architecture and contracts
Deliverables:
- architecture doc
- DSL v1 contract
- capability matrix
- policy model

To do:
- define Pipeline spec fields
- define canonical internal model
- define HVR and Informatica capability matrices
- define policy input object
- define persisted state model

Validation:
- design review
- model five representative example pipelines
- confirm each can be mapped or rejected clearly

### Phase 1: DSL and validation
Deliverables:
- YAML parser
- schema validation
- semantic validation
- validation CLI

To do:
- implement JSON Schema
- implement Go parser
- implement semantic validation rules
- create valid and invalid sample specs

Validation:
- unit tests
- golden fixtures
- human-readable error output

### Phase 2: Policy engine
Deliverables:
- OPA integration
- backend selection policy
- explainable decisions

To do:
- define policy input JSON
- write Rego rules for CDC and batch routing
- reject unsupported combinations
- return explanation output

Validation:
- table-driven tests
- policy explanation visible in CLI and CI

### Phase 3: Planner and compiler
Deliverables:
- backend-specific plan generation

To do:
- define plan model
- implement HVR compiler
- implement Informatica compiler
- generate diffs
- classify risk

Validation:
- golden tests
- deterministic plan generation
- manual review of plan readability

### Phase 4: Control plane API and state store
Deliverables:
- API service
- Postgres-backed state

To do:
- design database schema
- implement validate, plan, apply, and status APIs
- store spec versions, backend selection, plan, and state history

Validation:
- API contract tests
- migration tests
- persistence tests

### Phase 5: Temporal workflows
Deliverables:
- apply, verify, and delete workflows

To do:
- implement workflow types
- implement activities for backend calls
- implement retries and compensation
- map workflow states to lifecycle states

Validation:
- workflow tests
- retry tests
- idempotency tests
- simulated failure tests

### Phase 6: HVR adapter
Deliverables:
- CDC pipeline provisioning support

To do:
- implement auth and configuration handling
- map DSL semantics to HVR concepts
- implement create, update, read, and delete
- return clear unsupported feature errors

Validation:
- mocked adapter tests
- sandbox HVR integration tests

### Phase 7: Informatica adapter
Deliverables:
- batch pipeline provisioning support

To do:
- implement auth and configuration handling
- map DSL semantics to Informatica concepts
- implement create, update, read, and delete
- normalize backend errors

Validation:
- mocked adapter tests
- sandbox Informatica integration tests

### Phase 8: GitHub integration
Deliverables:
- PR validation and apply workflows

To do:
- build GitHub Actions for validate, policy, and plan
- publish plan summaries to PRs
- trigger apply on merge

Validation:
- end-to-end PR test
- invalid YAML test
- approval-gated change test

### Phase 9: Drift detection and observability
Deliverables:
- drift detection
- metrics, logs, traces

To do:
- implement periodic reconciliation
- emit Drifted state
- instrument services with OpenTelemetry
- publish operational dashboards if useful

Validation:
- simulate drift
- validate alerts and traces

### Phase 10: Production hardening
Deliverables:
- authn/authz
- auditability
- approval model
- secrets hardening

To do:
- secure backend credentials
- define RBAC
- implement audit logs
- enforce destructive-change approvals
- isolate environments

Validation:
- security review
- least-privilege review
- audit trail verification

## Initial implementation to-do list

### Foundations
- [ ] write architecture decision record for the control-plane model
- [ ] define DSL v1 fields
- [ ] create example specs for CDC, batch, and invalid cases
- [ ] define HVR capability matrix
- [ ] define Informatica capability matrix
- [ ] create initial JSON Schema

### Policy and planning
- [ ] define policy input model
- [ ] write initial Rego policies
- [ ] implement policy explanation output
- [ ] define internal plan model
- [ ] implement HVR compiler
- [ ] implement Informatica compiler

### Execution
- [ ] bootstrap Go service
- [ ] add Postgres-backed state store
- [ ] add Temporal worker
- [ ] implement apply workflow
- [ ] implement verification workflow

### Integrations
- [ ] implement HVR adapter auth and CRUD operations
- [ ] implement Informatica adapter auth and CRUD operations
- [ ] normalize backend errors into platform errors

### GitHub workflow
- [ ] build GitHub Action for validate and plan
- [ ] add PR comment output
- [ ] add apply-on-merge workflow

### Reliability
- [ ] add idempotency protections
- [ ] add drift detection worker
- [ ] add metrics, logging, and tracing
- [ ] create failure playbooks

## Validation strategy

### Unit validation
- schema validation tests
- semantic validation tests
- policy tests
- compiler tests
- adapter tests

### Integration validation
- HVR sandbox integration
- Informatica sandbox integration
- Temporal workflow execution
- Postgres persistence
- GitHub Actions validation flow

### End-to-end validation
Build and test:
1. one CDC pipeline, expected to route to HVR
2. one batch pipeline, expected to route to Informatica
3. one unsupported pipeline, expected to fail with a clear explanation

### Operational validation
- backend timeout handling
- partial apply failure handling
- retry behavior
- drift detection after manual backend changes
- destructive change approval gating

## Recommended repo structure

```text
/cmd
  /api
  /worker
  /cli
/internal
  /api
  /compiler
  /policy
  /planner
  /state
  /temporal
  /adapters
    /hvr
    /informatica
  /validation
  /reconcile
/rego
/schemas
/examples
/docs
/tests
```

## Questions to resolve before implementation

1. Who is the first user persona?
   - platform engineers
   - data engineers
   - analysts
   - app teams

2. Can users force backend selection, or only provide hints?

3. How expressive should transforms be in v1?
   - passthrough only
   - light transforms
   - arbitrary SQL or mappings

4. Will connections and credentials be pre-registered, or should this platform manage them?

5. Should this remain GitHub-only initially, or also expose API-first and UI workflows?

6. What is the first deployment scope?
   - internal platform
   - one business unit
   - enterprise-wide

7. Do HVR and Informatica expose mature enough APIs for the required automation?

## Final recommendation

Keep the stack of GitHub, GitHub Actions, Temporal, OPA, and Go.

Add:
- Postgres
- JSON Schema
- OpenTelemetry

And position the project as a declarative data pipeline control plane rather than only an ETL abstraction layer.

For the MVP, focus on:
- declarative YAML specs
- policy-based routing
- plan generation
- backend provisioning
- execution visibility
- a narrow, trustworthy slice rather than maximum abstraction
