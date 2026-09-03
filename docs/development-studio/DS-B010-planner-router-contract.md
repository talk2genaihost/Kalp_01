# DS-B010 — Planner / Router Contract

**Status:** PROPOSED / DERIVED  
**Version:** 0.1  
**Authority:** VERSIONED / ACTIVE CANDIDATE  
**Canonical:** NO

## Purpose

Define the minimum Development Studio planning boundary that transforms request/task context and registered routing metadata into an inspectable, declarative routing decision.

## Inputs

The planner/router may consume:

- request or task identity
- request class
- required capability, when explicitly known
- available candidate routing entries
- authority scope
- escalation conditions
- provenance/source references

The planner/router MUST NOT fabricate missing requirements, capabilities, workforce assignments, authority, or routing metadata.

## Output

A `PlanDecision` containing:

- decision identity
- task/request reference
- candidate route references considered
- selected route reference, only when justified by explicit conditions and no unresolved authority conflict
- unresolved conditions
- escalation requirements
- provenance/source references

A plan decision is not execution authorization.

## Selection Boundary

Selection MUST be deterministic and inspectable. If multiple materially equivalent candidates remain, or required context is missing, the planner/router MUST return an unresolved decision and/or escalation requirement rather than silently selecting a winner.

The planner/router MUST preserve candidate routes and their provenance so downstream governance can inspect the decision basis.

## Authority Boundary

Planning does not authorize execution. Authorization, invocation, policy adjudication, Department Head/persona override, and workforce governance remain outside this component.

The planner/router MUST preserve declared authority scope and escalation conditions and MUST NOT resolve a canonical authority conflict outside the governed authority path.

## Non-Goals

This contract does not define:

- Agent Runtime
- Tool Gateway
- Master Orchestrator
- execution or invocation
- authorization or policy enforcement
- replacement of the Global Workforce Registry
- automatic supersession of route/capability records
- hidden fallback routing
- fabricated routing metadata
- canonical KALP authority or promotion

## Acceptance Criteria

An implementation is acceptable when it:

1. consumes registered capability/routing metadata without mutating the registries;
2. produces an inspectable declarative decision;
3. preserves candidate route references and provenance;
4. refuses ambiguous selection rather than silently choosing a candidate;
5. separates planning from authorization and execution;
6. preserves authority and escalation metadata;
7. does not promote this derived contract to canonical authority.
