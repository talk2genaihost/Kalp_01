"""Bounded execution request/result boundary for Development Studio.

This module constructs and records execution boundary objects only. It does
not invoke agents or tools, schedule work, manage credentials, or execute
arbitrary code.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Literal, Mapping, Sequence
from uuid import uuid4

from .persistence.sqlite import SQLiteStore

ExecutionStatus = Literal["REQUESTED", "SUCCEEDED", "FAILED", "UNRESOLVED", "ESCALATED"]


@dataclass(frozen=True)
class ExecutionRequest:
    request_id: str = field(default_factory=lambda: f"exec_{uuid4().hex}")
    project_id: str = ""
    task_id: str | None = None
    plan_decision_ref: str = ""
    authorization_decision_ref: str = ""
    selected_route_ref: str = ""
    capability_ref: str = ""
    provider_type: str = ""
    provider_ref: str = ""
    inputs: Mapping[str, Any] = field(default_factory=dict)
    authorized_scope: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()
    escalation_conditions: tuple[str, ...] = ()
    provenance: tuple[str, ...] = ()
    status: ExecutionStatus = "REQUESTED"


@dataclass(frozen=True)
class ExecutionResult:
    execution_id: str = field(default_factory=lambda: f"execution_{uuid4().hex}")
    request_id: str = ""
    status: ExecutionStatus = "UNRESOLVED"
    outputs: Mapping[str, Any] = field(default_factory=dict)
    evidence_refs: tuple[str, ...] = ()
    failure_information: tuple[str, ...] = ()
    escalation_information: tuple[str, ...] = ()
    provenance: tuple[str, ...] = ()


class ExecutionBoundary:
    """Construct inspectable execution records without performing execution."""

    def __init__(self, store: SQLiteStore | None = None):
        self.store = store

    def create_request(
        self,
        *,
        project_id: str,
        plan_decision_ref: str,
        authorization_decision_ref: str,
        authorization_result: str,
        selected_route_ref: str,
        capability_ref: str,
        provider_type: str,
        provider_ref: str,
        inputs: Mapping[str, Any] | None = None,
        authorized_scope: Sequence[str] = (),
        constraints: Sequence[str] = (),
        escalation_conditions: Sequence[str] = (),
        provenance: Sequence[str] = (),
        task_id: str | None = None,
    ) -> ExecutionRequest:
        self._require_text(project_id, "project_id")
        self._require_text(plan_decision_ref, "plan_decision_ref")
        self._require_text(authorization_decision_ref, "authorization_decision_ref")
        self._require_text(selected_route_ref, "selected_route_ref")
        self._require_text(capability_ref, "capability_ref")
        self._require_text(provider_type, "provider_type")
        self._require_text(provider_ref, "provider_ref")
        if authorization_result != "AUTHORIZED":
            raise ValueError("execution requires an AUTHORIZED decision")
        if provider_type not in ("AGENT", "TOOL"):
            raise ValueError("provider_type must be AGENT or TOOL")
        if not authorized_scope:
            raise ValueError("authorized_scope is required")
        if not provenance:
            raise ValueError("provenance is required")

        request = ExecutionRequest(
            project_id=project_id,
            task_id=task_id,
            plan_decision_ref=plan_decision_ref,
            authorization_decision_ref=authorization_decision_ref,
            selected_route_ref=selected_route_ref,
            capability_ref=capability_ref,
            provider_type=provider_type,
            provider_ref=provider_ref,
            inputs=dict(inputs or {}),
            authorized_scope=tuple(dict.fromkeys(str(x) for x in authorized_scope)),
            constraints=tuple(dict.fromkeys(str(x) for x in constraints)),
            escalation_conditions=tuple(dict.fromkeys(str(x) for x in escalation_conditions)),
            provenance=tuple(dict.fromkeys(str(x) for x in provenance)),
        )
        if self.store is not None:
            record = asdict(request)
            record["id"] = request.request_id
            self.store.insert("execution_requests", record)
        return request

    def record_result(
        self,
        *,
        request_id: str,
        status: ExecutionStatus,
        outputs: Mapping[str, Any] | None = None,
        evidence_refs: Sequence[str] = (),
        failure_information: Sequence[str] = (),
        escalation_information: Sequence[str] = (),
        provenance: Sequence[str] = (),
    ) -> ExecutionResult:
        self._require_text(request_id, "request_id")
        if status not in ("SUCCEEDED", "FAILED", "UNRESOLVED", "ESCALATED"):
            raise ValueError("result status must be SUCCEEDED, FAILED, UNRESOLVED, or ESCALATED")
        if not provenance:
            raise ValueError("provenance is required")
        if self.store is not None and self.store.get("execution_requests", request_id) is None:
            raise LookupError(f"execution request not found: {request_id}")

        result = ExecutionResult(
            request_id=request_id,
            status=status,
            outputs=dict(outputs or {}),
            evidence_refs=tuple(dict.fromkeys(str(x) for x in evidence_refs)),
            failure_information=tuple(dict.fromkeys(str(x) for x in failure_information)),
            escalation_information=tuple(dict.fromkeys(str(x) for x in escalation_information)),
            provenance=tuple(dict.fromkeys(str(x) for x in provenance)),
        )
        if self.store is not None:
            record = asdict(result)
            record["id"] = result.execution_id
            self.store.insert("execution_results", record)
        return result

    @staticmethod
    def _require_text(value: str, field_name: str) -> None:
        if not str(value).strip():
            raise ValueError(f"{field_name} is required")

    # Deliberately no execute(), invoke(), authorize(), schedule(), or retry() API.
