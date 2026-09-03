"""Stage 9 Working-Agent Runtime integration boundary.

This module defines the narrow handoff between Development Studio's
ExecutionRequest records and an externally governed Agent Runtime.

It deliberately does not implement the runtime, credentials, scheduling,
agent/tool discovery, authorization, or actual invocation mechanism.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol, Sequence
from uuid import uuid4

from .execution_boundary import ExecutionRequest, ExecutionResult

RuntimeState = str


@dataclass(frozen=True)
class RuntimeSubmission:
    """Immutable handoff record sent to a governed Working-Agent Runtime."""

    submission_id: str = field(default_factory=lambda: f"run_{uuid4().hex}")
    request_id: str = ""
    agent_ref: str = ""
    capability_ref: str = ""
    provider_type: str = "AGENT"
    provider_ref: str = ""
    runtime_state: RuntimeState = "CREATED"
    inputs: Mapping[str, Any] = field(default_factory=dict)
    authorized_scope: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()
    provenance: tuple[str, ...] = ()


@dataclass(frozen=True)
class RuntimeOutcome:
    """Immutable runtime outcome mapped back to the Stage 8 result boundary."""

    request_id: str = ""
    runtime_state: RuntimeState = ""
    status: str = "UNRESOLVED"
    outputs: Mapping[str, Any] = field(default_factory=dict)
    evidence_refs: tuple[str, ...] = ()
    failure_information: tuple[str, ...] = ()
    escalation_information: tuple[str, ...] = ()
    provenance: tuple[str, ...] = ()


class WorkingAgentRuntimePort(Protocol):
    """Port implemented by a separately governed Agent Runtime."""

    def submit(self, submission: RuntimeSubmission) -> RuntimeOutcome:
        """Accept a governed submission and return its runtime outcome."""
        ...


class WorkingAgentRuntimeBoundary:
    """Adapt an authorized ExecutionRequest to a governed runtime port."""

    def prepare(self, request: ExecutionRequest) -> RuntimeSubmission:
        """Create a runtime handoff without executing the request."""
        self._validate_request(request)
        return RuntimeSubmission(
            request_id=request.request_id,
            agent_ref=request.provider_ref if request.provider_type == "AGENT" else "",
            capability_ref=request.capability_ref,
            provider_type=request.provider_type,
            provider_ref=request.provider_ref,
            inputs=dict(request.inputs),
            authorized_scope=request.authorized_scope,
            constraints=request.constraints,
            provenance=request.provenance,
        )

    def submit(self, request: ExecutionRequest, runtime: WorkingAgentRuntimePort) -> ExecutionResult:
        """Submit through an injected governed runtime and map its outcome.

        The boundary owns no runtime implementation. The supplied runtime must
        be separately governed; this adapter does not authorize or invoke it.
        """
        submission = self.prepare(request)
        outcome = runtime.submit(submission)
        if outcome.request_id != request.request_id:
            raise ValueError("runtime outcome request_id does not match execution request")
        if outcome.status not in ("SUCCEEDED", "FAILED", "UNRESOLVED", "ESCALATED"):
            raise ValueError("runtime outcome has invalid result status")
        return ExecutionResult(
            request_id=request.request_id,
            status=outcome.status,  # type: ignore[arg-type]
            outputs=dict(outcome.outputs),
            evidence_refs=tuple(dict.fromkeys(outcome.evidence_refs)),
            failure_information=tuple(dict.fromkeys(outcome.failure_information)),
            escalation_information=tuple(dict.fromkeys(outcome.escalation_information)),
            provenance=tuple(dict.fromkeys((*request.provenance, *outcome.provenance))),
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
        missing = [name for name, value in required.items() if not str(value).strip()]
        if missing:
            raise ValueError(f"execution request missing required runtime metadata: {', '.join(missing)}")
        if request.provider_type not in ("AGENT", "TOOL"):
            raise ValueError("provider_type must be AGENT or TOOL")
        if not request.authorized_scope:
            raise ValueError("authorized_scope is required")
        if not request.provenance:
            raise ValueError("provenance is required")

    # Deliberately no credentials, scheduling, discovery, authorization,
    # execute(), invoke(), or runtime implementation is owned here.
