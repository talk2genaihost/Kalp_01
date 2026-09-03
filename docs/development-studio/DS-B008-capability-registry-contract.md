# DS-B008 — Development Studio Capability Registry Contract

Status: PROPOSED / DERIVED
Version: 0.1
Authority: VERSIONED / REGISTERED / ACTIVE CANDIDATE after governed registration

## 1. Purpose

Define the minimum Development Studio capability-registry boundary required to discover and select available agent/tool capabilities without granting execution authority.

This contract is an implementation artifact under Development Studio. It does not establish a canonical KALP-wide Capability Registry and does not replace KALP policy, authority, workforce, persona, orchestration, or tool-governance sources.

## 2. Governed basis

This contract is derived from retrieved KALP orchestration evidence that identifies Capability Registry as a P0 implementation dependency and requires metadata for capabilities, agent/tool references, inputs, outputs, constraints and escalation conditions.

The KALP Master Orchestrator Contract further requires capability information including available Working Agents/tools, capabilities, required inputs, outputs, constraints, authority scope and escalation conditions.

## 3. Registry entry

Each capability entry MUST preserve, at minimum:

- capability_id
- name
- version
- description / purpose
- provider_type: AGENT | TOOL
- provider_ref
- required_inputs
- expected_outputs
- constraints
- authority_scope
- escalation_conditions
- status
- provenance / source_references

Optional implementation metadata may include ownership, risk class, budget profile, verification profile and supported execution modes when explicitly supplied by a governing source.

## 4. Capability discovery vs authorization

Registry presence means capability discovery only.

A registry entry MUST NOT be interpreted as permission to invoke an agent or tool.

Authorization remains a separate governance/runtime concern. A capability may be discoverable while execution remains denied, unavailable, approval-gated or otherwise constrained.

## 5. Identity and versioning

Capability identity and provider identity MUST remain inspectable.

A newer capability version MUST NOT automatically supersede an earlier version.

When multiple versions coexist, the registry preserves the family and records explicit supersession only when evidence exists.

## 6. Input/output contracts

Required inputs and expected outputs MUST be represented as declarative metadata.

The registry MUST NOT fabricate missing schemas. Unknown requirements remain explicit as unresolved or unavailable rather than being inferred into authoritative metadata.

## 7. Constraints and authority scope

Constraints MUST be preserved as part of capability metadata.

Authority scope identifies the domain or boundary within which the capability may be considered relevant. It is not an authorization grant.

Cross-domain authority conflicts MUST remain subject to the KALP governed resolution path.

## 8. Escalation conditions

A capability entry MAY declare conditions requiring clarification, governance review, approval, blocking or escalation.

The registry records these conditions; it does not itself adjudicate governance conflicts.

## 9. Provenance

Every registered capability entry MUST preserve source references sufficient to identify where its material metadata came from.

Derived registry entries MUST remain distinguishable from canonical source authority.

## 10. Lifecycle

Recommended lifecycle:

DISCOVERED → VALIDATED → REGISTERED → AVAILABLE → DEPRECATED / RETIRED

Lifecycle state MUST NOT be treated as authority promotion.

## 11. Non-goals

- No tool authorization engine.
- No agent runtime.
- No planner/router implementation.
- No Master Orchestrator implementation.
- No replacement of the KALP Global Workforce Registry.
- No canonical KALP-wide capability authority.
- No automatic supersession or deletion.

## 12. Acceptance boundary

A conforming Development Studio implementation must be able to:

1. Store capability metadata without losing provider identity.
2. Preserve required inputs and expected outputs.
3. Preserve constraints, authority scope and escalation conditions.
4. Distinguish capability discovery from authorization.
5. Preserve version-family lineage without recency-based supersession.
6. Preserve provenance/source references.
7. Represent unavailable or unresolved metadata explicitly.
8. Avoid silently deleting, merging or promoting capability records.
