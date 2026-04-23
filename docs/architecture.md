# Architecture

## Positioning

This system is best understood as a **policy-driven control plane for data movement**, not merely a thin abstraction layer over ETL tools.

That distinction matters because HVR and Informatica are not equivalent execution engines. They have different strengths, different abstractions, and different operational models. The platform should provide a common declarative interface while still acknowledging backend-specific reality.

## System goals

- define pipelines declaratively in YAML
- treat Git as the source of truth
- select execution backends through policy
- compile desired intent into backend-specific plans
- apply changes through reliable orchestration
- expose status, history, and drift clearly

## High-level architecture

The platform can be broken into nine layers.

### 1. DSL / Spec layer
User-authored YAML that describes desired pipeline intent.

Responsibilities:
- versioned API shape
- stable schema
- ownership and metadata
- desired source, target, semantics, and requirements
- references to named connections rather than embedded credentials

### 2. Validation and enrichment
Ensures the input is structurally and semantically valid before any policy or backend logic runs.

Responsibilities:
- schema validation
- semantic validation
- reference validation
- connection reference validation
- defaulting and canonicalization

### 3. Policy engine
Determines placement, approval rules, and compliance constraints.

Responsibilities:
- backend eligibility
- routing decisions
- compliance checks
- approval requirements
- explainable policy output
- connection usage policy evaluation

### 4. Compiler / planner
Maps the validated and policy-evaluated model into a backend-specific execution plan.

Responsibilities:
- convert abstract pipeline intent into backend operations
- classify create, update, delete, and no-op
- produce readable plans and diffs
- identify high-risk changes

### 5. Workflow orchestration
Executes long-running tasks against external systems.

Responsibilities:
- retries
- compensation
- polling for completion
- resumability
- lifecycle progression
- secure connection resolution during apply

### 6. Connection registry and lookup path
Separates connection metadata and secret resolution from the pipeline DSL.

Responsibilities:
- resolve `connectionRef`
- validate connection existence and environment fit
- enforce connection usage policy
- resolve secret references from a secrets manager
- return normalized connection material to adapters

### 7. Backend adapters
Encapsulate integration logic with each execution platform.

Initial adapters:
- HVR
- Informatica

Responsibilities:
- consume normalized resolved connection material
- CRUD operations against backend APIs
- capability checks
- state read-back for verification
- backend error normalization

### 8. Control plane API and state store
Stores pipeline state, execution history, plan metadata, and connection metadata.

Responsibilities:
- persist desired and observed state
- expose status APIs
- retain execution history
- support drift and audit workflows
- persist connection registry metadata

### 9. GitOps / CI integration
Connects repository workflows to validation, planning, and apply operations.

Responsibilities:
- validate pull requests
- produce plan previews
- trigger apply on merge
- report status back into GitHub

## Core control-plane flow

The system should use an explicit pipeline for every change:

1. parse
2. validate
3. resolve and validate references
4. enrich
5. evaluate policy
6. select backend
7. compile plan
8. resolve connections securely at apply time
9. apply plan
10. verify result
11. monitor for drift

Making these phases explicit will help a lot with debugging, user trust, and auditability.

## Technology fit

### Go
Use Go for the main implementation.

Good fit for:
- API service
- parser and validators
- compiler and planner
- Temporal workers
- backend adapters
- orchestration support code

### GitHub
Use GitHub as the source of truth for pipeline specs and review workflows.

Good fit for:
- pull requests
- branch-based promotion
- traceability
- collaboration and approvals

### GitHub Actions
Use Actions as CI/CD glue, not the long-running execution engine.

Good fit for:
- schema validation
- semantic checks
- policy checks
- plan generation
- pull request summaries
- apply triggers on merge

### Temporal
Temporal is a strong fit for execution.

Good fit for:
- long-running workflows
- retries and backoff
- async backend provisioning
- polling external systems
- resumability after failure
- compensation and cleanup logic

### OPA
OPA is a good fit for policy, especially backend selection and compliance rules.

Good fit for:
- CDC vs batch routing
- environment restrictions
- compliance requirements
- approval decisions
- explainable policy output

OPA should remain focused on policy, not become the whole application logic layer.

### Postgres
Use Postgres for control-plane state and connection metadata.

Good fit for:
- pipeline metadata
- execution history
- selected backend
- rendered plans
- observed state snapshots
- audit records
- connection registry metadata

### JSON Schema
Use JSON Schema for structural validation of the DSL.

Good fit for:
- schema enforcement
- versioned contracts
- CI validation
- editor tooling

### OpenTelemetry
Add OpenTelemetry early for visibility.

Good fit for:
- traces across API, planner, workflows, and adapters
- metrics for throughput and failures
- operational debugging

## Architectural principles

### Git is the source of truth
Pipeline definitions should live in Git and drive the system.

### Intent is separate from implementation
Users declare outcomes. The platform decides how to realize them.

### Connection material is separate from pipeline intent
Pipelines should reference named connections. Secrets and credential material should be resolved through a registry and secrets-backed lookup path.

### Policy decides placement
Backend selection should be visible and testable policy, not hidden conditional logic.

### Lowest common denominator is not enough
Use a common core, but allow backend-specific extensions when necessary.

### Orchestration must be idempotent
Every workflow should be safe to retry.

### Observability is a feature
Users need to understand:
- why a backend was chosen
- what plan was produced
- what happened during apply
- what the current lifecycle state is

## Suggested service boundaries

A practical starting layout:

- spec parser / validator
- policy service
- planner / compiler
- connection registry / resolver module
- control plane API
- Temporal worker service
- HVR adapter module
- Informatica adapter module
- reconciliation worker

This can begin as one repository and possibly one deployable service plus workers, then separate later if needed.
