# DS-B010 — Development Studio Planner / Router Boundary Contract

Status: PROPOSED / DERIVED
Version: 0.1
Authority: VERSIONED / ACTIVE CANDIDATE only; not canonical

## 1. Purpose

Define the minimum Development Studio planning boundary that transforms an existing task/request context into a declarative routing decision using registered capability and routing metadata.

This contract does not establish a canonical KALP planner, router or Master Orchestrator.

## 2. Governed basis

This boundary follows the established Development Studio sequence: domain and state/event persistence, artifact/lineage, capability discovery, and Department / Working-Agent candidate routing. Existing DS-B008 and DS-B009 boundaries explicitly exclude planner/router execution and authorization.

No canonical DS-B010 source was found in the accessible repository. This contract is therefore derived and must not be represented as canonical.

## 3. Inputs

A planning request MUST preserve:

- request/task identity
- request class
- required capability, when known
- available candidate routing entries
- relevant authority scope
- escalation conditions
- provenance/source references

The planner MUST NOT fabricate missing requirements, capability metadata, workforce identity or authority.

## 4. Output

The planner returns a declarative `PlanDecision` containing:

- decision_id
- task/request reference
- candidate route references
- selected route reference, only when selection is justified by explicit selection conditions and there is no unresolved authority conflict
- unresolved conditions
- escalation requirements
- provenance

A plan decision is not an execution authorization.

## 5. Selection semantics

Selection must be deterministic with respect to the supplied registry state and explicit selection conditions.

If multiple candidates remain materially equivalent, or required context is missing, the planner MUST return an unresolved/escalation outcome rather than silently selecting a winner.

## 6. Governance boundary

The planner may apply declarative routing conditions. It MUST NOT:

- grant authorization
- invoke agents or tools
- override Department Head/persona governance
- replace the Global Workforce Registry
- resolve canonical authority conflicts outside the governed resolution path
- create or promote canonical KALP authority

## 7. Versioning and provenance

Input capability and routing versions remain inspectable. The planner must not mutate or supersede registry records.

Every decision preserves the source references used to reach it.

## 8. Non-goals

- Agent Runtime
- Tool Gateway
- Master Orchestrator
- Authorization engine
- Workforce/persona registry replacement
- Automatic supersession
- Hidden fallback or fabricated routing

## 9. Acceptance boundary

A conforming implementation must:

1. consume registered capability/routing metadata;
2. produce an inspectable declarative decision;
3. preserve candidate routes and provenance;
4. refuse unsupported or ambiguous selection rather than inventing a winner;
5. distinguish planning from authorization and execution;
6. preserve authority and escalation boundaries;
7. avoid mutating registry source records.
