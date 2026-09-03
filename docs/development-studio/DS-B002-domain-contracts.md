# DS-B002 — Development Studio Domain Contracts

Status: PROPOSED / DERIVED
Version: 0.1

## Purpose

Define the domain boundary for Development Studio without introducing runtime orchestration authority.

## Core entities

Project: project identity, user intent, platform, deployment mode, lifecycle state, requirements, tasks, artifacts and trace references.

Requirement: requirement identity, project association, description, source, status, dependencies, approval state and traceability.

Task: task identity, project association, capability reference, assignment, dependencies, state, inputs, outputs, failure and retry metadata.

AgentAssignment: assignment identity, task, capability/agent reference, execution status and provenance.

Dependency: explicit source/target relationship with dependency type and integrity metadata.

Artifact: versioned project output with type, creator, lineage, integrity, source references and validation status.

Build: build identity, project association, input/output references and build status.

TestRun: test identity/type, target, execution status, result and evidence.

Approval: approval identity, type, required state, decision, actor, reason and timestamp.

Retry: retry identity, target, failure classification, attempt number, outcome and reason.

Checkpoint: project execution milestone, snapshot/reference and timestamp.

Release: release identity, version, artifact set, validation state, approval state and release lifecycle state.

Event: immutable historical state transition/event record with actor, reason, inputs, outputs and source references.

## Deployment modes

- OFFLINE
- ONLINE
- HYBRID

Supported platform values are constrained by actual runtime/toolchain availability; acceptance of a platform in a domain contract does not imply buildability.

## Governance boundary

These are implementation contracts only. They do not establish KALP canonical authority and do not create a second Master Orchestrator.
