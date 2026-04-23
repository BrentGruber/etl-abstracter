# Sandbox

This directory contains the Phase 0 local sandbox for Euclid.

## Purpose

The sandbox is meant to give the project a repeatable local environment for validating:
- backend assumptions
- CDC flows
- batch / sync flows
- seeded source data
- recurring generated updates

It is not intended to be production-grade infrastructure. It is a development and design harness for Phase 0 and early Phase 1 work.

## Included services

- `postgres-source`
  - source database with seeded customer data
- `postgres-destination`
  - destination database for replication/sync tests
- `zookeeper`
- `kafka`
- `kafka-connect`
  - Debezium-compatible Kafka Connect worker
- `kafka-ui`
  - local visibility into Kafka topics and connectors
- `airbyte-db`
  - internal metadata database for Airbyte
- `airbyte-server`
- `airbyte-webapp`
- `data-generator`
  - inserts synthetic updates into the source database on an interval

## Current intent

This first pass is scaffolding.

It establishes:
- service layout
- seed data
- recurring source changes
- a home for future connector/bootstrap scripts

It does **not** yet fully automate:
- Debezium connector registration
- Airbyte source/destination/connection bootstrap
- end-to-end replication wiring

Those are the next logical Phase 0 follow-ups.

## Startup

```bash
docker compose -f sandbox/docker-compose.yml up -d
```

## Useful local endpoints

- Airbyte web UI: `http://localhost:8000`
- Airbyte server API: `http://localhost:8001`
- Kafka Connect: `http://localhost:8083`
- Kafka UI: `http://localhost:8085`
- source Postgres: `localhost:5433`
- destination Postgres: `localhost:5434`

## Seeded source data

The source Postgres instance creates a `customers` table and inserts a few initial rows.

## Generated updates

The `data-generator` service inserts synthetic customer rows every 15 seconds by default.

You can change the interval with:
- `UPDATE_INTERVAL_SECONDS`

## Recommended next steps

1. add Debezium connector bootstrap script
2. add Airbyte source/destination/connection bootstrap script
3. add a Makefile or helper scripts for common sandbox tasks
4. add sample pipeline specs that map directly onto this environment
5. add reset/teardown guidance and test scenarios
