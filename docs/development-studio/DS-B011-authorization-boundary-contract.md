# DS-B011 Authorization Boundary Contract

## Status

**PROPOSED / DERIVED**

## Version

0.1

## Authority

- Authority level: VERSIONED / ACTIVE CANDIDATE only.
- Canonical KALP authority: **NO**.
- This document is a derived implementation contract based on the current Development Studio stage lineage and explicit architectural boundaries.
- It must not be promoted to canonical status without an authoritative source decision.

## Purpose

Define the minimum Development Studio boundary for evaluating whether an existing, inspectable `PlanDecision` may proceed to a separately governed execution layer.

The boundary converts a plan decision plus explicitly supplied authorization context into an authorization outcome. It does not execute the plan.

## Inputs

The authorization boundary may consume only explicitly supplied information:

- plan/decision identity;
- selected route reference, when present;
- requested capability, when present;
- authority scope;
- authorization context and applicable constraints;
- escalation conditions;
- provenance/source references.

Missing authorization information must remain missing. The boundary must not fabricate permissions, identities, scopes, approvals, or policy decisions.

## Output

The boundary produces an inspectable authorization decision containing:

- decision identity;
- source plan decision reference;
- authorization result: `AUTHORIZED`, `DENIED`, `ESCALATE`, or `UNRESOLVED`;
- authorized scope when explicitly established;
- unresolved conditions;
- escalation requirements;
- provenance/source references.

## Core Rules

1. A `PlanDecision` is not an authorization.
2. Authorization does not imply execution.
3. Authorization must be based only on explicit supplied authority information.
4. Missing or conflicting authority information results in `UNRESOLVED` or `ESCALATE`, not an inferred approval.
5. A plan without a selected route cannot become authorized for execution.
6. Authorization scope must not exceed the explicitly supplied authority scope.
7. Provenance must be preserved.
8. The authorization boundary must not mutate capability or routing registries.
9. The authorization boundary must not invoke agents or tools.
10. No hidden fallback or implicit privilege escalation is permitted.

## Separation of Concerns

This contract establishes the boundary:

`Plan Decision -> Authorization Decision -> [future] Execution`

The authorization boundary does not become:

- Agent Runtime;
- Tool Gateway;
- Master Orchestrator;
- Workforce Registry;
- persona authority;
- general policy engine;
- execution engine.

## Non-Goals

This contract does not define:

- agent or tool invocation;
- execution scheduling;
- runtime orchestration;
- credential management;
- enterprise IAM replacement;
- canonical KALP governance policy;
- automatic approval;
- automatic escalation resolution;
- silent conflict resolution;
- route supersession;
- workforce/persona replacement.

## Acceptance Boundary

A conforming implementation must:

- accept an existing plan decision;
- require an explicit selected route for authorization;
- preserve plan and provenance references;
- distinguish authorization from execution;
- return unresolved/escalation outcomes when authority is insufficient or ambiguous;
- never invent authorization;
- avoid registry mutation;
- expose no agent/tool execution API.

## Provenance

Derived from the current Development Studio Stage 6 bounded planner/router boundary and its explicit separation from authorization and execution. No canonical DS-B011 source was available at registration time.
