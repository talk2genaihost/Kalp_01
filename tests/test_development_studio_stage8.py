import inspect

import pytest

from development_studio.execution_boundary import ExecutionBoundary, ExecutionRequest, ExecutionResult
from development_studio.persistence.sqlite import SQLiteStore


def authorized_kwargs():
    return {
        "project_id": "PRJ-1",
        "plan_decision_ref": "PLAN-1",
        "authorization_decision_ref": "AUTH-1",
        "authorization_result": "AUTHORIZED",
        "selected_route_ref": "ROUTE-1",
        "capability_ref": "CAP-1",
        "provider_type": "AGENT",
        "provider_ref": "agent.requirements",
        "inputs": {"requirements": {"id": "REQ-1"}},
        "authorized_scope": ["development-studio"],
        "constraints": ["read-only"],
        "escalation_conditions": ["missing-input"],
        "provenance": ["plan:PLAN-1", "auth:AUTH-1"],
        "task_id": "TASK-1",
    }


def test_authorized_plan_constructs_inspectable_request():
    store = SQLiteStore()
    request = ExecutionBoundary(store).create_request(**authorized_kwargs())
    assert isinstance(request, ExecutionRequest)
    assert request.status == "REQUESTED"
    assert request.plan_decision_ref == "PLAN-1"
    assert request.authorization_decision_ref == "AUTH-1"
    assert request.selected_route_ref == "ROUTE-1"
    assert request.provider_ref == "agent.requirements"
    assert store.get("execution_requests", request.request_id)["authorized_scope"] == ["development-studio"]


def test_non_authorized_plan_cannot_become_execution_request():
    kwargs = authorized_kwargs()
    kwargs["authorization_result"] = "DENIED"
    with pytest.raises(ValueError, match="AUTHORIZED"):
        ExecutionBoundary().create_request(**kwargs)


def test_missing_required_execution_metadata_is_rejected():
    kwargs = authorized_kwargs()
    kwargs["selected_route_ref"] = ""
    with pytest.raises(ValueError, match="selected_route_ref"):
        ExecutionBoundary().create_request(**kwargs)


def test_result_requires_traceable_request_when_persisted():
    boundary = ExecutionBoundary(SQLiteStore())
    with pytest.raises(LookupError, match="execution request not found"):
        boundary.record_result(
            request_id="missing",
            status="SUCCEEDED",
            provenance=["runtime:evidence-1"],
        )


def test_result_preserves_status_outputs_evidence_and_provenance():
    store = SQLiteStore()
    boundary = ExecutionBoundary(store)
    request = boundary.create_request(**authorized_kwargs())
    result = boundary.record_result(
        request_id=request.request_id,
        status="SUCCEEDED",
        outputs={"artifact": "ART-1"},
        evidence_refs=["evidence:ART-1"],
        provenance=["runtime:run-1"],
    )
    assert isinstance(result, ExecutionResult)
    assert result.status == "SUCCEEDED"
    saved = store.get("execution_results", result.execution_id)
    assert saved["request_id"] == request.request_id
    assert saved["evidence_refs"] == ["evidence:ART-1"]


def test_failure_and_escalation_are_distinct_from_success():
    store = SQLiteStore()
    boundary = ExecutionBoundary(store)
    request = boundary.create_request(**authorized_kwargs())
    failed = boundary.record_result(
        request_id=request.request_id,
        status="FAILED",
        failure_information=["provider failure"],
        provenance=["runtime:run-2"],
    )
    escalated = boundary.record_result(
        request_id=request.request_id,
        status="ESCALATED",
        escalation_information=["human review required"],
        provenance=["runtime:run-3"],
    )
    assert failed.status == "FAILED"
    assert escalated.status == "ESCALATED"


def test_boundary_does_not_execute_invoke_schedule_or_retry():
    public = [name for name, value in inspect.getmembers(ExecutionBoundary, inspect.isfunction) if not name.startswith("_")]
    assert public == ["create_request", "record_result"]
    boundary = ExecutionBoundary()
    assert not hasattr(boundary, "execute")
    assert not hasattr(boundary, "invoke")
    assert not hasattr(boundary, "schedule")
    assert not hasattr(boundary, "retry")
