# ETL Abstracter

A policy-driven control plane for declarative data pipelines.

## What this is

ETL Abstracter is a GitOps-native system for managing data pipelines as code. Users declare pipelines in YAML, and the platform validates them, evaluates policy, chooses an execution backend, and provisions the resulting pipeline through the appropriate tool.

The initial backend routing goal is simple:
- CDC pipelines should route to HVR
- batch pipelines should route to Informatica

## Why this exists

Most enterprise data platforms accumulate multiple integration tools with overlapping responsibilities. That creates inconsistency, tool sprawl, and a lot of manual decision-making.

This project aims to provide:
- a single declarative interface for pipeline intent
- policy-based backend selection
- Git-based review and promotion workflows
- long-running, reliable orchestration
- clear status, auditability, and drift detection

## Core idea

Users define the desired pipeline, not the exact tool implementation.

Pipelines reference named connections rather than embedding credentials. Connection details are resolved separately through a registry and secrets-backed lookup path.

The platform performs an explicit control-plane workflow:
1. parse YAML
2. validate schema and semantics
3. validate references and policy
4. select backend
5. compile a backend-specific plan
6. resolve connections securely at apply time
7. apply via orchestrated workflows
8. verify and track resulting state

## Proposed stack

- Go
- GitHub
- GitHub Actions
- Temporal
- OPA
- Postgres
- JSON Schema
- OpenTelemetry

## Design principles

- Git is the source of truth
- separate intent from implementation
- policy decides placement
- support a common core plus backend-specific extensions
- keep orchestration idempotent and resumable
- expose decision traces and execution status
- require review for destructive or high-risk changes

## MVP scope

The first version should focus on a narrow, trustworthy slice:
- one `Pipeline` DSL kind
- HVR and Informatica backends only
- simple routing policy
  - CDC -> HVR
  - batch -> Informatica
- plan generation in CI
- apply on merge
- execution tracking
- no rich UI initially

## Docs

- [Architecture](docs/architecture.md)
- [Roadmap](docs/roadmap.md)
- [DSL and Workflows](docs/dsl-and-workflows.md)
- [Proposed DSL Schema](docs/dsl-schema.md)
- [Backend Capabilities Matrix](docs/capabilities-matrix.md)
- [Connection Model and Lookup Service](docs/connection-model.md)
- [Long-Term Vision](docs/long-term-vision.md)

## Open questions

A few foundational questions still need answers before implementation:
- who is the first user persona?
- can users force backend selection or only hint?
- how expressive should transforms be in v1?
- are connections and credentials pre-registered?
- is GitHub the only interface at first?
- how mature are the HVR and Informatica APIs for automation?

## Current recommendation

Position this as a **declarative data pipeline control plane**, not just an ETL abstraction layer.

That framing is more accurate, scales better as more backends are added, and makes the policy/compiler/orchestrator architecture much easier to reason about.
