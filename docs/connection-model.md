# Connection Model and Lookup Service

## Goal

Separate pipeline intent from connection material.

Pipelines should describe:
- what data to move
- which named connections to use
- how the movement should behave

Pipelines should **not** contain:
- usernames
- passwords
- tokens
- private keys
- DSNs
- raw URLs when those are sensitive

That data should live behind a connection registry and secrets manager integration.

## Why this separation matters

### Security
Credentials should not live in pipeline specs or Git.

### Reuse
Many pipelines will reuse the same source and target systems.

### Governance
The platform can enforce which teams and environments may use which connections.

### Rotation and maintenance
If a password changes or an endpoint moves, update the connection once instead of editing many pipelines.

## Recommended architecture

Use three distinct concepts:

### 1. Pipeline resource
Contains business intent and operational behavior.

Examples:
- source object
- target object
- CDC vs batch semantics
- truncate vs append vs merge
- schedule
- schema policy
- governance

### 2. Connection registry
Contains connection metadata and references to secret material.

Examples:
- connection type
- environment
- endpoint metadata
- allowed usage
- secret references
- capability metadata

### 3. Secrets manager
Contains actual secret values.

Examples:
- username
- password
- token
- certificate
- private key
- DSN if required

## Recommended v1 approach

For v1, the simplest practical model is:
- store connection metadata in the control plane database
- store credential material in a secrets manager
- let pipelines reference connections by `connectionRef`

That gives a good balance between simplicity and clean separation.

## Pipeline usage pattern

The pipeline DSL should reference connections like this:

```yaml
sources:
  - name: erp-customers
    connectionRef: oracle-prod-customers
    object:
      schema: customer
      table: customers
    readMode:
      type: cdc

targets:
  - name: snowflake-customers
    connectionRef: snowflake-analytics-prod
    object:
      database: analytics
      schema: raw
      table: customers
    writeMode:
      type: merge
      keyFields:
        - customer_id
```

The pipeline still controls movement behavior such as:
- append vs merge vs overwrite
- scheduling
- retry behavior
- schema policy
- quality checks

But the connection details stay external.

## Proposed `Connection` resource

```yaml
apiVersion: platform.data/v1alpha1
kind: Connection
metadata:
  name: oracle-prod-customers
  labels: {}
  annotations: {}

spec:
  type: oracle
  environment: prod
  endpoint:
    host: oracle-prod.internal
    port: 1521
    database: CUSTOMER
  auth:
    secretRef: secret://vault/data/connections/oracle-prod-customers
  options:
    ssl: true
  governance:
    classification: confidential
    approvedTeams:
      - data-platform
      - finance-data
  capabilities:
    supportsCdc: true
    supportsBatch: true
```

## Proposed `Connection` fields

### Identity and metadata
- `metadata.name`
- `labels`
- `annotations`

### `spec.type`
Examples:
- `oracle`
- `sqlserver`
- `postgres`
- `snowflake`
- `s3`
- `kafka`

### `spec.environment`
Examples:
- `dev`
- `stage`
- `prod`

### `spec.endpoint`
Examples:
- `host`
- `port`
- `database`
- `account`
- `region`
- `bucket`
- `bootstrapServers`

Note: this may be partially metadata-only and partially sensitive depending on the environment.

### `spec.auth`
Examples:
- `secretRef`
- `authType`
- `credentialProfileRef`

### `spec.options`
Safe non-secret connection options.

Examples:
- `ssl`
- `sslMode`
- `warehouse`
- `role`
- `defaultSchema`

### `spec.governance`
Examples:
- `approvedTeams[]`
- `approvedEnvironments[]`
- `classification`
- `requiresApproval`

### `spec.capabilities`
Examples:
- `supportsCdc`
- `supportsBatch`
- `supportsSnapshot`
- `supportsMerge`

This field can help policy and planning but should not be treated as a substitute for runtime validation.

## Lookup service design

## Responsibilities
A connection lookup service should:
- resolve `connectionRef`
- return connection metadata
- resolve secret references securely
- enforce access policy
- provide normalized connection material to adapters

## Suggested interface
Conceptually:

- input:
  - `connectionRef`
  - requester identity
  - environment
- output:
  - normalized connection metadata
  - resolved auth material or short-lived access token
  - policy decision about whether access is allowed

## Resolution flow
1. pipeline spec references `connectionRef`
2. planner validates the referenced connection exists
3. policy engine checks whether the pipeline may use that connection
4. apply workflow resolves the connection through the lookup service
5. lookup service retrieves secrets from the secrets manager
6. adapter receives only the normalized material it needs

## Implementation options

### Option A: control plane resolves everything directly
The control plane reads both connection metadata and secrets.

Pros:
- simplest implementation

Cons:
- broad secret access in one component
- tighter coupling

### Option B: dedicated connection lookup service
A separate internal service owns resolution and secret access.

Pros:
- cleaner security boundary
- more reusable across systems

Cons:
- one more service to build and operate

### Option C: registry in DB, secrets in manager, shared resolver library
A middle-ground approach where the control plane owns the registry and a resolver module handles secret access.

Pros:
- simple for v1
- can later become a service

Cons:
- less explicit boundary initially

## Recommendation
Start with Option C.

It gives a clean model without introducing unnecessary operational overhead too early.

## Policy opportunities

Separating connections enables strong policy controls, for example:
- only approved teams may use certain prod connections
- PII pipelines may only use approved encrypted connections
- dev pipelines may not write to prod targets
- batch-only connections may not be used for CDC
- some connections may require manual approval

## Impact on the pipeline DSL

The pipeline DSL should prefer:
- `connectionRef`
- `object`
- `readMode` or `writeMode`

The pipeline DSL should avoid:
- raw credentials
- raw secrets
- embedded connection URLs unless intentionally non-sensitive

## Recommended resource set

Over time, the platform will likely want at least:
- `Pipeline`
- `Connection`
- possibly `PolicyProfile`
- possibly `EnvironmentProfile`

This is a cleaner long-term foundation than putting connection material directly inside pipeline specs.
