"""Bounded runtime coordination and execution-control boundary.

Derived from DS-B013. This module coordinates an already-authorized execution
request with an injected Working-Agent runtime port. It does not authorize,
discover, schedule, or implement unrestricted execution.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping
from uuid import uuid4

from .execution_boundary import ExecutionRequest
from .working_agent_runtime import RuntimeOutcome, WorkingAgentRuntimePort

CONTROL_TERMINAL = {
    "COMPLETED", "FAILED", "UNRESOLVED", "ESCALATED",
    "CANCELLED", "TIMED_OUT", "BUDGET_EXCEEDED",
}


@dataclass(frozen=True)
class CoordinationRecord:
    coordination_id: str = field(default_factory=lambda: f"coord_{uuid4().hex}")
    request_id: str = ""
    state: str = "CREATED"
    outcome_status: str = "UNRESOLVED"
    outputs: Mapping[str, Any] = field(default_factory=dict)
    evidence_refs: tuple[str, ...] = ()
    failure_information: tuple[str, ...] = ()
    escalation_information: tuple[str, ...] = ()
    provenance: tuple[str, ...] = ()
    state_history: tuple[str, ...] = ("CREATED",)


class RuntimeCoordinator:
    """Coordinate one authorized execution request through a governed runtime port."""

    def __init__(self) -> None:
        self._accepted: set[str] = set()

    def coordinate(self, request: ExecutionRequest, runtime: WorkingAgentRuntimePort) -> CoordinationRecord:
        self._validate_request(request)
        if request.request_id in self._accepted:
            raise ValueError(f"execution request already accepted: {request.request_id}")
        self._accepted.add(request.request_id)

        submission = request_to_submission(request)
        try:
            outcome = runtime.submit(submission)
        except Exception as exc:
            return CoordinationRecord(
                request_id=request.request_id,
                state="FAILED",
                outcome_status="FAILED",
                failure_information=(f"runtime submission failed: {type(exc).__name__}: {exc}",),
                provenance=request.provenance,
                state_history=("CREATED", "INITIALIZING", "READY", "SUBMITTED", "RUNNING", "FAILED"),
            )

        self._validate_outcome(request.request_id, outcome)
        terminal = self._map_terminal(outcome)
        return CoordinationRecord(
            request_id=request.request_id,
            state=terminal,
            outcome_status=outcome.status,
            outputs=outcome.outputs,
            evidence_refs=outcome.evidence_refs,
            failure_information=outcome.failure_information,
            escalation_information=outcome.escalation_information,
            provenance=tuple(dict.fromkeys((*request.provenance, *outcome.provenance))),
            state_history=("CREATED", "INITIALIZING", "READY", "SUBMITTED", "RUNNING", terminal),
        )

    @staticmethod
    def _validate_request(request: ExecutionRequest) -> None:
        required = {
            "request_id": request.request_id,
            "plan_decision_ref": request.plan_decision_ref,
            "authorization_decision_ref": request.authorization_decision_ref,
            "selected_route_ref": request.selected_route_ref,
            "capability_ref": request.capability_ref,
            "provider_ref": request.provider_ref,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise ValueError(f"missing execution metadata: {', '.join(missing)}")
        if request.provider_type != "AGENT":
            raise ValueError("RuntimeCoordinator requires an AGENT provider for Working-Agent runtime")
        if not request.authorized_scope:
            raise ValueError("authorized_scope is required")
        if request.status != "REQUESTED":
            raise ValueError(f"execution request is not coordinatable in status {request.status}")
        if not request.provenance:
            raise ValueError("provenance is required")

    @staticmethod
    def _validate_outcome(request_id: str, outcome: RuntimeOutcome) -> None:
        if outcome.request_id != request_id:
            raise ValueError("runtime outcome request identity does not match execution request")
        if outcome.status not in {"SUCCEEDED", "FAILED", "UNRESOLVED", "ESCALATED"}:
            raise ValueError(f"unsupported runtime outcome status: {outcome.status}")

    @staticmethod
    def _map_terminal(outcome: RuntimeOutcome) -> str:
        if outcome.status == "SUCCEEDED":
            return "COMPLETED"
        return outcome.status


def request_to_submission(request: ExecutionRequest):
    """Adapt an authorized Stage 8 request to the Stage 9 runtime integration port."""
    from .working_agent_runtime import RuntimeSubmission

    return RuntimeSubmission(
        request_id=request.request_id,
        agent_ref=request.provider_ref,
        capability_ref=request.capability_ref,
        provider_type=request.provider_type,
        provider_ref=request.provider_ref,
        inputs=request.inputs,
        authorized_scope=request.authorized_scope,
        constraints=request.constraints,
        provenance=request.provenance,
    )
