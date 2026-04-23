# Backend Capabilities Matrix

## Purpose

This matrix is a planning tool for deciding which parts of the DSL belong in the common model, which should be policy inputs, and which should remain backend-specific.

This is intentionally approximate for now. It should be refined once the concrete automation capabilities of HVR and Informatica are validated against their real APIs and operational models.

## Support scale

- **Strong**: natural fit for the backend
- **Partial**: possible, but with limitations or caveats
- **Weak**: awkward or narrow support
- **Unknown**: needs validation against real product/API behavior

## Summary view

| Capability area | HVR | Informatica | Notes |
| --- | --- | --- | --- |
| CDC replication | Strong | Partial | HVR is the obvious first-class CDC backend |
| Scheduled batch | Weak | Strong | Informatica is the natural batch-oriented backend |
| Initial snapshot/bootstrap | Strong | Partial | Both can likely support variants, but HVR is a better natural fit alongside CDC |
| Incremental batch loads | Partial | Strong | Informatica likely better for timer-based incremental jobs |
| Continuous low-latency movement | Strong | Partial | Strong routing input toward HVR |
| Complex transformations | Weak | Strong | Common DSL should stay narrow here |
| Passthrough replication | Strong | Partial | Strong HVR fit |
| Multi-source joins/unions | Weak | Strong | Informatica likely better suited |
| Schema evolution handling | Partial | Partial | Needs concrete validation on both sides |
| Upsert / merge delivery | Partial | Strong | Likely easier and richer on Informatica side |
| Data quality rules | Weak | Partial | May need platform-managed checks rather than backend-native checks |
| Governance / policy enforcement | Platform | Platform | Best handled by control plane + OPA |
| Long-running orchestration | Platform | Platform | Best handled by Temporal |
| Drift detection | Platform | Platform | Best handled by control plane |

## Detailed matrix

| DSL area | Capability / knob | HVR | Informatica | Control-plane note |
| --- | --- | --- | --- | --- |
| Ownership | ownerTeam, approvers, runbook | Platform | Platform | Should be platform-only metadata |
| Sources | single source table/object | Strong | Strong | Common model |
| Sources | multiple sources | Partial | Strong | Good policy signal |
| Sources | source filters / predicates | Partial | Strong | May require backend-specific expression handling |
| Sources | CDC read mode | Strong | Partial | Strong routing input |
| Sources | snapshot read mode | Strong | Strong | Common model |
| Sources | incremental read mode | Partial | Strong | Strong routing input |
| Targets | single target table/object | Strong | Strong | Common model |
| Targets | multiple targets | Partial | Strong | Policy and compiler concern |
| Targets | file/object-store targets | Unknown | Partial | Needs validation |
| Targets | queue/topic targets | Unknown | Partial | Needs validation |
| Semantics | `mode=cdc` | Strong | Partial | Strong HVR signal |
| Semantics | `mode=batch` | Weak | Strong | Strong Informatica signal |
| Semantics | `mode=snapshot` | Partial | Strong | Likely both possible |
| Semantics | `mode=incremental` | Partial | Strong | More natural for batch backend |
| Semantics | delete propagation | Strong | Partial | Important correctness knob |
| Semantics | preserve history / SCD2 | Weak | Strong | Likely not a good HVR-first capability |
| Semantics | near-real-time SLA | Strong | Partial | Good routing input |
| Execution | continuous trigger | Strong | Partial | HVR-oriented |
| Execution | cron schedule | Weak | Strong | Informatica-oriented |
| Execution | manual trigger | Partial | Strong | Both likely possible in some form |
| Execution | retries / timeouts | Platform | Platform | Should be handled primarily in Temporal |
| Execution | dependency chaining | Weak | Strong | Likely better in control plane or Informatica |
| Transform | passthrough | Strong | Strong | Common v1 capability |
| Transform | projection / rename / cast | Partial | Strong | Maybe common with compiler restrictions |
| Transform | filter | Partial | Strong | Needs careful abstraction |
| Transform | joins | Weak | Strong | Strong signal toward Informatica |
| Transform | aggregations | Weak | Strong | Strong signal toward Informatica |
| Transform | mappingRef / sqlRef | Weak | Strong | Better as backend-specific or constrained common field |
| Delivery | append | Partial | Strong | Common model |
| Delivery | merge / upsert | Partial | Strong | Strong routing input |
| Delivery | overwrite / replace | Weak | Strong | More batch-oriented |
| Delivery | partitioning | Weak | Partial | Likely depends on target and backend |
| Delivery | batching knobs | Weak | Strong | Often backend-specific |
| Schema | strict enforcement | Partial | Partial | Needs validation |
| Schema | add columns automatically | Partial | Partial | Needs validation |
| Schema | breaking change policy | Weak | Partial | Better enforced by control plane |
| Quality | rowcount checks | Weak | Partial | Could be platform-managed |
| Quality | null / uniqueness checks | Weak | Partial | Could be platform-managed |
| Quality | reconciliation | Weak | Partial | Likely platform concern |
| Governance | classification, residency, encryption | Platform | Platform | OPA + control plane concern |
| Observability | alerts, dashboards, lineage metadata | Partial | Partial | Likely hybrid, but best surfaced by platform |
| Backend hints | preferred backend | N/A | N/A | Used by planner/policy, not backend directly |
| Backend extensions | backend-native knobs | Strong | Strong | Keep isolated from common schema |

## Key implications for the DSL

## 1. The common model should stay focused on intent
The shared schema should cover:
- sources
- targets
- movement semantics
- execution model
- delivery behavior
- schema policy
- governance
- ownership

That gives policy and planning enough signal without overfitting to any one backend.

## 2. Transformation should stay constrained early
A rich transformation language will quickly bias the DSL toward Informatica-like capabilities.

Recommendation:
- v1 should support passthrough and very light transforms only
- richer transform logic should either be deferred or referenced externally

## 3. Governance should live in the platform, not the backends
Security, residency, approval, and environment restrictions are better enforced by:
- OPA
- control-plane validation
- Git review workflows

That keeps enforcement consistent regardless of backend.

## 4. Reliability should be platform-managed
Retries, backoff, compensation, and lifecycle state should live primarily in Temporal and the control plane rather than being modeled as backend-native behavior.

## 5. Some knobs should be routing signals, not universal capabilities
Examples:
- `mode=cdc`
- `latencySla=near-real-time`
- `transform` complexity
- `execution.trigger=schedule`
- `delivery.mode=merge`
- `historyMode=scd2`

These are important because they help select the right backend.

## Suggested v1 capability boundary

### Strong candidates for common v1 fields
- one to many sources and targets
- pipeline mode
- trigger mode
- basic delivery mode
- key fields
- schema evolution policy
- governance requirements
- ownership metadata
- backend hints

### Better deferred or restricted in v1
- complex joins and aggregations
- rich data quality frameworks
- very backend-specific optimization knobs
- advanced multi-stage graph execution
- complex lineage authoring in the DSL

## Validation tasks to refine this matrix

Before locking the DSL or planner behavior, validate the following:

### HVR validation tasks
- confirm API support for create/update/delete flows
- validate how initial load plus CDC is modeled
- validate delete propagation semantics
- validate supported targets and merge semantics
- validate whether schema evolution can be observed and controlled

### Informatica validation tasks
- confirm API support for provisioning batch mappings and workflows
- validate scheduling and incremental load capabilities
- validate support for merge/upsert semantics
- validate support for transformations from a declarative mapping model
- validate how much state can be read back cleanly for reconciliation

### Cross-platform validation tasks
- determine where quality checks should actually run
- determine whether schema policy belongs in planner logic or backend config
- define a minimal common transform model that both sides can tolerate
- define clear rejection rules for unsupported combinations

## Final recommendation

Use this matrix to drive three decisions:
1. what belongs in the common DSL
2. what belongs in `backendExtensions`
3. what belongs in platform policy instead of either backend

That separation will keep the system understandable and prevent the DSL from collapsing into a vague least-common-denominator format.
