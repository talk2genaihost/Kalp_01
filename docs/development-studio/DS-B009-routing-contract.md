# DS-B009 — Development Studio Department / Working-Agent Routing Contract

Status: PROPOSED / DERIVED
Version: 0.1
Authority: VERSIONED / REGISTERED / ACTIVE CANDIDATE only if separately registered; not canonical

## 1. Purpose

Define the minimum Development Studio routing boundary that maps a request class and, where available, a required capability to the governed department / Working-Agent references that may be considered for task assignment.

This is an implementation artifact under Development Studio. It does not replace the KALP Global Workforce Registry, Department Heads, persona governance, policy, authorization, planner/router, or Master Orchestrator.

## 2. Governed basis

This contract is derived from the registered Master Orchestrator Implementation & Dependency Map, which identifies Department / Working-Agent routing as the next dependency after the Capability Registry and requires mapping request classes to minimum required departments/agents.

The orchestration blueprint establishes that the Orchestrator routes and coordinates while Department Heads provide domain governance and Working Agents execute. Existing workforce/persona sources remain authoritative within their own scopes.

## 3. Routing entry

Each routing entry MUST preserve, at minimum:

- route_id
- request_class
- capability_id, when a capability constraint is known
- department_ref, when a governed department reference is known
- agent_ref, when a governed Working-Agent reference is known
- selection_conditions
- authority_scope
- escalation_conditions
- status
- provenance / source_references

Unknown or unavailable references remain explicit. The routing layer MUST NOT fabricate department, persona or agent identities.

## 4. Routing vs execution authority

A routing entry expresses candidate applicability only.

Presence in the routing registry MUST NOT be interpreted as authorization to execute, invoke a tool, or override a governing Department Head/persona.

Authorization, approval and execution remain separate runtime/governance concerns.

## 5. Workforce and persona authority

Routing may reference existing governed workforce/persona identifiers, but MUST NOT overwrite, normalize away, merge or replace their source authority.

A public-personality alignment source MUST NOT be treated as a replacement for an actual KALP Department Head merely because it is available for routing context.

## 6. Selection semantics

The registry records routing candidates and declarative selection conditions. It does not implement a planner, optimization engine, execution coordinator or Master Orchestrator.

Where multiple candidates apply, the routing layer preserves the candidates rather than silently selecting an authoritative winner.

## 7. Versioning and lineage

A newer route definition MUST NOT automatically supersede an earlier definition.

Distinct route identities and versions remain inspectable. Explicit supersession requires evidence.

## 8. Provenance

Every routing entry MUST preserve source references sufficient to identify the evidence for its material routing metadata.

Derived routing entries MUST remain distinguishable from canonical workforce/persona and governance sources.

## 9. Lifecycle

Recommended lifecycle:

DISCOVERED → VALIDATED → REGISTERED → AVAILABLE → DEPRECATED / RETIRED

Lifecycle state MUST NOT be treated as authority promotion.

## 10. Non-goals

- No planner/router execution engine.
- No Master Orchestrator.
- No agent runtime.
- No authorization or policy engine.
- No replacement of the KALP Global Workforce Registry.
- No replacement of Department Heads or persona governance.
- No automatic route supersession.
- No silent merge of conflicting workforce/persona records.

## 11. Acceptance boundary

A conforming Development Studio implementation must be able to:

1. Store request-class routing metadata without losing governed references.
2. Preserve capability, department and Working-Agent references.
3. Preserve selection conditions, authority scope and escalation conditions.
4. Distinguish candidate routing from authorization/execution.
5. Preserve route version identity without recency-based supersession.
6. Preserve provenance/source references.
7. Represent unknown or unavailable references explicitly.
8. Preserve multiple applicable candidates without silently choosing a winner.
