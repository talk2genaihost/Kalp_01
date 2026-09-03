# DS-B003 — Development Studio Project and Task State Contract

Status: PROPOSED / DERIVED
Version: 0.1

## Project lifecycle

CREATED → DISCOVERY → REQUIREMENTS → REQUIREMENTS_APPROVED → ARCHITECTURE → DESIGN → IMPLEMENTATION_PLANNED → IMPLEMENTING → BUILDING → TESTING → VALIDATION → RELEASE_READY → DELIVERED

## Exceptional project states

BLOCKED, AWAITING_CLARIFICATION, FAILED, UNRESOLVED, UNAVAILABLE

## Task lifecycle

PENDING → READY → ASSIGNED → EXECUTING → COMPLETED

Exceptional branches: FAILED, BLOCKED, AWAITING_CLARIFICATION, UNRESOLVED.

## Rules

1. State transitions must be centrally defined and validated.
2. Invalid transitions must be rejected rather than silently coerced.
3. Project/task state is distinct from KALP orchestration state.
4. REQUIREMENTS_APPROVED is not automatic; approval is explicit.
5. UNAVAILABLE represents missing capability, tool, environment, source or other required execution dependency where applicable.
6. Historical transitions must be traceable through events.

This contract does not implement a planner, scheduler, dependency executor or Master Orchestrator.
