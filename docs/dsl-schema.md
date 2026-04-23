# Proposed DSL Schema

## Goal

This document proposes a full DSL shape for declarative data pipeline definitions.

The intent is to give data engineers enough control to describe real pipelines while keeping backend selection, planning, and enforcement inside the platform.

This is a **proposed schema model**, not a finalized implementation contract.

## Design principles

The DSL should:
- express user intent clearly
- keep common concepts in a shared core
- allow backend-specific extensions when necessary
- separate policy inputs from backend implementation details
- support validation, planning, and explainable rejection

## Resource model

### Top-level shape

```yaml
apiVersion: platform.data/v1alpha1
kind: Pipeline
metadata:
  name: customer-erp-to-warehouse
  labels: {}
  annotations: {}

spec:
  ownership: {}
  sources: []
  targets: []
  semantics: {}
  execution: {}
  transform: {}
  delivery: {}
  schema: {}
  quality: {}
  governance: {}
  observability: {}
  backendHints: {}

backendExtensions: {}
```

## Top-level fields

### `apiVersion`
Schema/API version.

### `kind`
Resource kind. Initially:
- `Pipeline`

### `metadata`
Identity and metadata for the resource.

Proposed fields:
- `name`
- `labels`
- `annotations`

### `spec`
Desired pipeline intent.

### `backendExtensions`
Optional backend-specific configuration that should be allowed only when necessary.

---

# `spec` sections

## 1. `ownership`

Captures who owns, supports, and approves the pipeline.

Example:

```yaml
ownership:
  ownerTeam: data-platform
  businessDomain: customer
  contacts:
    - type: slack
      value: '#data-platform'
    - type: email
      value: data-platform@example.com
  costCenter: finance-analytics
  criticality: high
  runbookUrl: https://example.internal/runbooks/customer-pipeline
```

Proposed fields:
- `ownerTeam`
- `businessDomain`
- `contacts[]`
  - `type`
  - `value`
- `costCenter`
- `criticality`
  - `low`
  - `medium`
  - `high`
  - `critical`
- `runbookUrl`
- `approvers[]`

Why it matters:
- ownership and support routing
- approval policy
- operational accountability

## 2. `sources`

One to many source definitions.

Example:

```yaml
sources:
  - name: erp-customers
    system: oracle-prod
    type: oracle
    connectionRef: oracle-prod-customers
    object:
      database: null
      schema: customer
      table: customers
    readMode:
      type: cdc
      initialLoad: true
    keys:
      primaryKey:
        - customer_id
```

Proposed fields per source:
- `name`
- `system`
- `type`
- `connectionRef`
- `object`
  - `database`
  - `schema`
  - `table`
  - `view`
  - `queryRef`
- `readMode`
  - `type`
    - `cdc`
    - `snapshot`
    - `batch`
    - `incremental`
  - `initialLoad`
  - `incrementalField`
  - `watermarkStrategy`
- `filter`
  - `sqlWhere`
  - `predicateRef`
- `keys`
  - `primaryKey[]`
  - `businessKey[]`
- `options`
  - backend-specific neutral hints

Why it matters:
- backend compatibility
- movement semantics
- merge/upsert behavior
- snapshot vs incremental planning

## 3. `targets`

One to many targets.

Example:

```yaml
targets:
  - name: snowflake-raw-customers
    system: snowflake-prod
    type: snowflake
    connectionRef: snowflake-raw
    object:
      database: analytics
      schema: raw
      table: customers
    writeMode:
      type: merge
      keyFields:
        - customer_id
```

Proposed fields per target:
- `name`
- `system`
- `type`
- `connectionRef`
- `object`
  - `database`
  - `schema`
  - `table`
  - `path`
  - `topic`
- `writeMode`
  - `type`
    - `append`
    - `merge`
    - `overwrite`
    - `snapshotReplace`
  - `keyFields[]`
  - `partitionFields[]`
- `options`

Why it matters:
- merge strategy
- file/table/topic delivery shape
- correctness semantics

## 4. `semantics`

Describes pipeline behavior at a high level.

Example:

```yaml
semantics:
  mode: cdc
  topology: one_to_many
  deletePropagation: true
  preserveHistory: true
  historyMode: scd2
  orderingRequired: true
  latencySla: near-real-time
```

Proposed fields:
- `mode`
  - `cdc`
  - `batch`
  - `snapshot`
  - `incremental`
  - `stream`
- `topology`
  - `one_to_one`
  - `one_to_many`
  - `many_to_one`
  - `many_to_many`
- `deletePropagation`
- `preserveHistory`
- `historyMode`
  - `none`
  - `audit`
  - `scd1`
  - `scd2`
- `orderingRequired`
- `latencySla`
  - `best-effort`
  - `hourly`
  - `sub-hour`
  - `near-real-time`
- `bootstrapRequired`
- `backfillSupported`

Why it matters:
- core policy routing input
- backend capability alignment
- lifecycle and data correctness semantics

## 5. `execution`

Controls when and how work runs.

Example:

```yaml
execution:
  trigger:
    type: schedule
    cron: '0 * * * *'
    timezone: UTC
  retries:
    maxAttempts: 5
    backoff: exponential
  timeoutMinutes: 60
  concurrency:
    policy: forbid
    maxParallelRuns: 1
  catchup:
    enabled: true
    maxIntervals: 24
```

Proposed fields:
- `trigger`
  - `type`
    - `continuous`
    - `schedule`
    - `event`
    - `manual`
  - `cron`
  - `timezone`
  - `eventRef`
- `retries`
  - `maxAttempts`
  - `backoff`
- `timeoutMinutes`
- `concurrency`
  - `policy`
    - `allow`
    - `forbid`
    - `queue`
  - `maxParallelRuns`
- `catchup`
  - `enabled`
  - `maxIntervals`
- `dependsOn[]`

Why it matters:
- operational behavior
- workflow orchestration
- scheduling vs continuous routing

## 6. `transform`

Describes transformation intent.

Example:

```yaml
transform:
  type: projection
  operations:
    - type: select
      columns:
        - customer_id
        - email
        - created_at
    - type: rename
      from: created_at
      to: created_timestamp
    - type: cast
      column: created_timestamp
      dataType: timestamp
```

Proposed fields:
- `type`
  - `passthrough`
  - `projection`
  - `sql`
  - `mappingRef`
- `operations[]`
  - `select`
  - `rename`
  - `cast`
  - `derive`
  - `filter`
  - `join`
  - `aggregate`
  - `deduplicate`
- `sqlRef`
- `mappingRef`
- `udfRefs[]`

Recommendation:
- keep this narrow in v1
- support passthrough and light transforms first

## 7. `delivery`

Describes target write semantics.

Example:

```yaml
delivery:
  mode: merge
  keyFields:
    - customer_id
  partitioning:
    strategy: day
    fields:
      - created_date
  batching:
    maxRows: 10000
    maxBytesMb: 64
  guarantees:
    idempotent: true
    deliverySemantics: at-least-once
```

Proposed fields:
- `mode`
  - `append`
  - `merge`
  - `overwrite`
  - `replace`
- `keyFields[]`
- `partitioning`
  - `strategy`
  - `fields[]`
- `batching`
  - `maxRows`
  - `maxBytesMb`
- `guarantees`
  - `idempotent`
  - `deliverySemantics`
    - `best-effort`
    - `at-least-once`
    - `exactly-once-like`

Why it matters:
- target correctness
- platform planning
- backend-specific tuning

## 8. `schema`

Defines schema management policy.

Example:

```yaml
schema:
  evolution:
    mode: add-columns
    allowNullableExpansion: true
    allowTypeWidening: false
  onBreakingChange: fail
  columnMappingMode: explicit
```

Proposed fields:
- `evolution`
  - `mode`
    - `strict`
    - `add-columns`
    - `compatible-only`
  - `allowNullableExpansion`
  - `allowTypeWidening`
- `onBreakingChange`
  - `fail`
  - `pause`
  - `manualApproval`
- `columnMappingMode`
  - `auto`
  - `explicit`
- `columns[]`
  - optional explicit schema declarations

Why it matters:
- one of the biggest real-world pain points
- strong input to both policy and backend selection

## 9. `quality`

Defines validation and reconciliation requirements.

Example:

```yaml
quality:
  checks:
    - type: rowcount
      tolerancePercent: 1
    - type: not_null
      columns:
        - customer_id
    - type: uniqueness
      columns:
        - customer_id
  onFailure:
    action: fail
    quarantineTarget: rejected_customers
```

Proposed fields:
- `checks[]`
  - `rowcount`
  - `not_null`
  - `uniqueness`
  - `freshness`
  - `customRuleRef`
- `onFailure`
  - `action`
    - `warn`
    - `fail`
    - `quarantine`
  - `quarantineTarget`

Why it matters:
- trust in pipeline outputs
- operational safety
- platform policy hooks

## 10. `governance`

Security, compliance, and data policy inputs.

Example:

```yaml
governance:
  classification: pii
  encryptionRequired: true
  residency: us
  maskSensitiveFields: true
  approvedEnvironments:
    - prod
    - stage
```

Proposed fields:
- `classification`
  - `public`
  - `internal`
  - `confidential`
  - `pii`
  - `phi`
- `encryptionRequired`
- `residency`
- `maskSensitiveFields`
- `approvedEnvironments[]`
- `credentialRefs[]`

Why it matters:
- direct input to OPA policy
- environment restrictions
- approval requirements

## 11. `observability`

Operational expectations for visibility and alerts.

Example:

```yaml
observability:
  metrics:
    enabled: true
  alerts:
    onFailure: true
    onLagThresholdMinutes: 15
  lineage:
    enabled: true
  dashboardRef: customer-pipeline-dashboard
```

Proposed fields:
- `metrics.enabled`
- `alerts.onFailure`
- `alerts.onLagThresholdMinutes`
- `lineage.enabled`
- `dashboardRef`
- `logLevel`

Why it matters:
- operating pipelines in production
- clear ownership and SLOs

## 12. `backendHints`

Optional hints that influence backend choice but do not override policy automatically.

Example:

```yaml
backendHints:
  preferredBackend: auto
  latencyPriority: high
  costSensitivity: medium
```

Proposed fields:
- `preferredBackend`
  - `auto`
  - `hvr`
  - `informatica`
- `latencyPriority`
- `costSensitivity`
- `operationalSimplicityPriority`

Recommendation:
- hints should not bypass hard policy
- they can influence selection when multiple backends are eligible

---

# `backendExtensions`

Backend-specific fields should live outside the common `spec` when possible.

Example:

```yaml
backendExtensions:
  hvr:
    integrateMethod: log-based
    channelTemplate: standard-cdc
  informatica:
    runtimeEnvironment: prod-iics
    mappingTemplate: batch-standard
```

Rules for backend extensions:
- use only when the common model cannot express the need
- validate only when the corresponding backend is selected or explicitly requested
- keep them isolated from the core schema

---

# Example full resource

```yaml
apiVersion: platform.data/v1alpha1
kind: Pipeline
metadata:
  name: customer-erp-to-warehouse

spec:
  ownership:
    ownerTeam: data-platform
    businessDomain: customer
    criticality: high

  sources:
    - name: erp-customers
      system: oracle-prod
      type: oracle
      connectionRef: oracle-prod-customers
      object:
        schema: customer
        table: customers
      readMode:
        type: cdc
        initialLoad: true
      keys:
        primaryKey:
          - customer_id

  targets:
    - name: snowflake-raw-customers
      system: snowflake-prod
      type: snowflake
      connectionRef: snowflake-raw
      object:
        database: analytics
        schema: raw
        table: customers
      writeMode:
        type: merge
        keyFields:
          - customer_id

  semantics:
    mode: cdc
    topology: one_to_one
    deletePropagation: true
    preserveHistory: true
    historyMode: scd2
    orderingRequired: true
    latencySla: near-real-time

  execution:
    trigger:
      type: continuous
    retries:
      maxAttempts: 5
      backoff: exponential
    timeoutMinutes: 60

  transform:
    type: passthrough

  delivery:
    mode: merge
    keyFields:
      - customer_id
    guarantees:
      idempotent: true
      deliverySemantics: at-least-once

  schema:
    evolution:
      mode: add-columns
      allowNullableExpansion: true
      allowTypeWidening: false
    onBreakingChange: fail

  quality:
    checks:
      - type: not_null
        columns:
          - customer_id
      - type: uniqueness
        columns:
          - customer_id
    onFailure:
      action: fail

  governance:
    classification: pii
    encryptionRequired: true
    residency: us

  observability:
    metrics:
      enabled: true
    alerts:
      onFailure: true
      onLagThresholdMinutes: 15

  backendHints:
    preferredBackend: auto
    latencyPriority: high

backendExtensions:
  hvr:
    integrateMethod: log-based
```

## Recommendation for implementation phases

### Good v1 fields
- `ownership`
- `sources`
- `targets`
- `semantics`
- `execution`
- `transform` with narrow support
- `delivery`
- `schema`
- `governance`
- `backendHints`

### Add later
- richer `quality`
- richer `observability`
- advanced multi-stage pipeline graphs
- deeper backend extensions

## Final note

The DSL should remain focused on **intent and constraints**, not become a programming language.

That will make policy evaluation, backend selection, planning, and long-term maintenance much saner.
