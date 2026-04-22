# DSL and Workflows

## DSL design goals

The DSL should express user intent without forcing users to understand the detailed object model of each backend.

At the same time, it should not pretend all backends are identical. The right balance is:
- a common core for shared concepts
- backend-specific extensions where needed
- explicit validation and rejection when a pipeline cannot be represented safely

## Recommended DSL structure

The DSL should separate:
- identity and ownership
- source and target systems
- semantics
- requirements and constraints
- policy hints
- backend-specific extensions

## Example DSL

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

## Recommended field categories

### Metadata
- name
- owner
- tags
- environment
- business domain

### Source
- system identifier
- technology type
- location details
- object identifiers such as schema and table

### Target
- system identifier
- technology type
- location details
- object identifiers such as database, schema, and table

### Semantics
- mode such as CDC or batch
- latency SLA
- ordering requirements
- delete propagation rules
- history requirements

### Requirements
- encryption
- residency
- retention
- compliance classification
- operational constraints

### Policy hints
- preferred backend
- latency priority
- cost sensitivity

### Backend extensions
- HVR-specific settings
- Informatica-specific settings

## Initial policy examples

Useful first routing policies:
- if `semantics.mode == cdc`, route to HVR
- if `semantics.mode == batch`, route to Informatica
- if a backend cannot support the declared source or target, reject
- if compliance constraints are not satisfied, reject
- if a change is destructive, require approval

## Proposed lifecycle state machine

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

### Typical flow
1. Draft
2. Validating
3. PolicyEvaluating
4. Planned
5. AwaitingApproval when needed
6. Provisioning
7. Verifying
8. Active

### Failure and maintenance transitions
- Provisioning -> Failed
- Verifying -> Failed
- Active -> Updating
- Active -> Drifted
- Active -> Deleting -> Deleted

## Proposed user workflows

## 1. Create a new pipeline
1. author YAML in Git
2. open a pull request
3. CI validates the spec
4. CI evaluates policy and selects a backend
5. CI generates a plan preview
6. reviewers approve
7. merge triggers apply
8. Temporal provisions the backend resources
9. verification confirms success
10. status is published back to GitHub

## 2. Update a pipeline
1. modify the YAML spec
2. CI computes a diff and updated plan
3. risky changes trigger approval requirements
4. merge triggers the update workflow
5. verification confirms the new state

## 3. Delete a pipeline
1. remove or disable the YAML definition
2. CI produces a deletion plan
3. approval is required if the change is destructive
4. merge triggers deprovisioning
5. the pipeline transitions to Deleted

## 4. Drift handling
1. reconcile workers inspect backend state periodically
2. observed state is compared to desired state
3. drift marks the pipeline as Drifted
4. policy determines whether to alert, require review, or auto-reconcile

## Technology mapping by workflow

### GitHub and GitHub Actions
Used for:
- authoring workflow
- PR review
- validation
- planning
- apply triggers

### OPA
Used for:
- backend selection
- compliance rules
- approval requirements
- explainable decisions

### Temporal
Used for:
- apply workflows
- verification workflows
- deletion workflows
- retry and compensation behavior

### Go services
Used for:
- parsing
- validation
- compilation
- API handling
- worker logic
- adapters

### Postgres
Used for:
- lifecycle state
- execution history
- plan storage
- observed state records

## Open design questions

Questions worth resolving early:
- should users be able to force a backend?
- how much transform logic belongs in v1?
- are connections managed here or elsewhere?
- what level of backend-specific override is acceptable?
- what should be considered a destructive change?

## Recommendation for v1

Keep the first DSL narrow.

Good v1 scope:
- source
- target
- semantics
- requirements
- policy hints
- optional backend extensions

Avoid in v1:
- rich transformation programming
- advanced multi-step orchestration embedded in the DSL
- trying to normalize every backend feature into the common model
