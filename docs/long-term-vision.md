# Long-Term Vision

## From ETL abstraction to data control plane

The near-term goal of this project is to provide a declarative control plane for data movement, where users define pipelines in YAML and the platform selects the appropriate backend such as HVR or Informatica.

The longer-term opportunity is larger.

This system can evolve from an ETL abstraction layer into a broader **data control plane** that manages how enterprise data is:
- connected
- moved
- modeled
- governed
- consumed
- traced through lineage

That means the project should be designed around **resources and references**, not just around ETL jobs.

## Proposed long-term resource model

A useful way to think about the platform is in layers.

### 1. Connectivity layer
Defines how the platform reaches systems securely.

Potential resources:
- `Connection`
- `CredentialProfile`
- `EnvironmentProfile`

Responsibilities:
- connection metadata
- secret resolution
- environment scoping
- allowed usage and governance

### 2. Data movement layer
Defines how data moves between systems.

Potential resources:
- `Pipeline`
- `PipelineTemplate`
- `BackfillJob`

Responsibilities:
- source and target references
- movement semantics
- scheduling and execution
- delivery rules
- backend selection and provisioning

### 3. Semantic layer
Defines business-facing meaning on top of curated data assets.

Potential resources:
- `SemanticLayer`
- `Metric`
- `SemanticModel`
- `Dimension`

Responsibilities:
- dimensions and measures
- business entities
- join rules
- grain definitions
- ownership and semantic contracts

### 4. Consumption layer
Defines or registers downstream reporting and analytics assets.

Potential resources:
- `Report`
- `Dashboard`
- `DatasetExposure`

Responsibilities:
- report metadata
- ownership and certification
- external BI tool references
- downstream lineage and impact analysis

### 5. Governance and quality layer
Defines policies, controls, and trust mechanisms.

Potential resources:
- `PolicyProfile`
- `QualityCheck`
- `Certification`

Responsibilities:
- classification
- residency and encryption rules
- approval controls
- data quality expectations
- certification state

## Why this model matters

## 1. It creates a real control plane
Instead of only answering:
- which ETL tool should create this pipeline?

The platform can eventually answer:
- what is this asset?
- who owns it?
- where did it come from?
- how is it transformed?
- what semantic contract does it expose?
- what reports depend on it?

## 2. It enables derived lineage
Once resources reference one another, lineage can be inferred from the model.

Example chain:
- source connection and object
- pipeline
- target dataset
- semantic layer object
- report object

That is much more scalable than manually curating lineage edges everywhere.

## 3. It supports governance propagation
Ownership, classification, quality expectations, and certification can propagate through the graph.

For example:
- a PII source can mark downstream assets as sensitive
- an uncertified semantic model can prevent a report from being marked certified
- an upstream breaking change can trigger downstream impact analysis

## Long-term resource relationship model

A simple conceptual graph:

- `Connection` provides access to systems
- `Pipeline` reads from and writes to datasets via `Connection` references
- `SemanticLayer` depends on physical or curated datasets
- `Report` depends on a `SemanticLayer` or dataset
- lineage is derived from these references

## Example lineage chain

1. `Connection/oracle-prod-customers`
2. source object `customer.customers`
3. `Pipeline/customer-erp-to-warehouse`
4. `Connection/snowflake-analytics-prod`
5. target object `raw.customers`
6. `SemanticLayer/customer-revenue`
7. `Report/executive-customer-revenue`

This gives the platform enough structure to answer:
- where did this report come from?
- which pipelines feed this semantic model?
- what breaks if this source changes?

## Proposed future resources

## `SemanticLayer`
This is the most natural resource to add after pipelines.

A semantic layer object could define:
- upstream dataset references
- entities
- grain
- dimensions
- measures
- ownership
- governance and freshness expectations

Example shape:

```yaml
apiVersion: platform.data/v1alpha1
kind: SemanticLayer
metadata:
  name: customer-revenue

spec:
  ownership:
    ownerTeam: analytics-engineering

  source:
    datasetRef: snowflake.analytics.marts.customer_revenue

  model:
    primaryEntity: customer
    grain:
      - customer_id
      - revenue_date

    dimensions:
      - name: customer_id
        type: string
      - name: region
        type: string
      - name: revenue_date
        type: date

    measures:
      - name: total_revenue
        expression: sum(revenue_amount)
        type: number
      - name: customer_count
        expression: count_distinct(customer_id)
        type: number

  governance:
    classification: confidential
```

Why it is a good next step:
- still strongly declarative
- fits resource-and-reference modeling well
- provides a clean lineage bridge between pipelines and reporting

## `Report`
Reports are trickier to manage fully as code, but still useful as a resource.

A `Report` object does not need to mean full visual layout provisioning on day one. It can start as a registration and lineage object.

A report object could define:
- owner
- reporting tool
- external object reference
- semantic or dataset dependencies
- certification state
- freshness or SLA expectations

Example shape:

```yaml
apiVersion: platform.data/v1alpha1
kind: Report
metadata:
  name: executive-customer-revenue

spec:
  ownership:
    ownerTeam: finance-analytics

  tool: tableau
  externalRef: tableau://workbook/customer-revenue/executive-view

  dependsOn:
    - semanticLayerRef: customer-revenue

  governance:
    certified: true
    classification: confidential

  operational:
    sla: daily
```

## Realistic maturity model for reports

### Level 1: report registration
Track:
- external IDs
- owners
- dependencies
- certification
- governance
- lineage

This is very achievable and already valuable.

### Level 2: partial report config as code
Track:
- dataset bindings
- semantic model references
- refresh settings
- some permissions or tags

This may be possible depending on the reporting tool.

### Level 3: full report as code
Track:
- layout
- charts
- filters
- formatting
- interactions

This is much harder and very tool-specific. It should not be an early requirement.

## Lineage model

Lineage should be derived wherever possible.

Prefer this:
- resources reference other resources or datasets
- the platform builds a graph from those references

Avoid this where possible:
- humans authoring explicit lineage edges for everything

Derived lineage can still support optional annotations later, but the default should be automatic graph construction from resource references.

## Suggested rollout order

### Phase 1
- `Connection`
- `Pipeline`

### Phase 2
- derived lineage graph from pipeline references
- basic asset catalog views
- governance and ownership propagation

### Phase 3
- `SemanticLayer`
- metrics and dimension contracts
- semantic lineage

### Phase 4
- `Report` as metadata and lineage registration
- optional partial report configuration support

### Phase 5
- broader catalog, impact analysis, and quality integration
- certification workflows
- more advanced semantic governance

## Important architectural implication

This project should be designed around a canonical notion of **assets and references**, not just jobs.

That means:
- pipelines produce or update data assets
- semantic resources depend on data assets
- reports depend on semantic resources or datasets
- lineage is a graph derived from references between these resources

If this is modeled well from the start, the platform can grow naturally from ETL orchestration into a broader declarative data platform.

## Naming implication

Today, the repo name `etl-abstracter` is fine as a working starting point.

Long-term, the architecture is really moving toward something closer to:
- data control plane
- declarative data platform
- data graph control plane

That does not require an immediate rename, but it is worth keeping in mind as the scope expands.

## Recommendation

Build the first version around `Connection` and `Pipeline`, but keep the internal model flexible enough to add:
- `SemanticLayer`
- `Report`
- derived lineage
- governance propagation

That path gives the project a much stronger strategic ceiling than stopping at backend routing for ETL jobs.
