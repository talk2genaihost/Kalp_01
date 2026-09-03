# DS-B004 — Development Studio Event Model Contract

Status: PROPOSED / DERIVED
Version: 0.1

## Event record

An event records a material state transition or execution event and preserves provenance.

Required fields:

- EVENT_ID
- PROJECT_ID
- TASK_ID where applicable
- TIMESTAMP
- PREVIOUS_STATE where applicable
- NEW_STATE where applicable
- ACTOR
- REASON
- INPUTS where applicable
- OUTPUTS where applicable
- SOURCE_REFERENCES where applicable

## Rules

- Events are historical records and should not be mutated to rewrite history.
- State changes must be reconstructable from recorded events where the runtime uses event-backed state.
- Material decisions and governance actions must retain source/provenance references.
- Event semantics must remain distinct from KALP's own orchestration event semantics until an explicit integration contract exists.

This is a contract, not an event bus implementation.
