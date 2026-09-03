from development_studio.execution_boundary import ExecutionBoundary
from development_studio.runtime_coordinator import RuntimeCoordinator
from development_studio.agent_runtime import InProcessWorkingAgentRuntime


def make_request():
    return ExecutionBoundary().create_request(
        project_id="p1",
        plan_decision_ref="plan-1",
        authorization_decision_ref="auth-1",
        authorization_result="AUTHORIZED",
        selected_route_ref="route-1",
        capability_ref="cap-1",
        provider_type="AGENT",
        provider_ref="agent-1",
        inputs={"x": 2},
        authorized_scope=("execute:task",),
        provenance=("stage11-test",),
    )


def test_coordinates_authorized_request_and_preserves_traceability():
    request = make_request()
    runtime = InProcessWorkingAgentRuntime({"agent-1": lambda inputs: {"y": inputs["x"] * 2}})
    record = RuntimeCoordinator().coordinate(request, runtime)

    assert record.state == "COMPLETED"
    assert record.outcome_status == "SUCCEEDED"
    assert record.outputs == {"y": 4}
    assert record.request_id == request.request_id
    assert record.provenance == ("stage11-test",)
    assert record.state_history == ("CREATED", "INITIALIZING", "READY", "SUBMITTED", "RUNNING", "COMPLETED")


def test_duplicate_submission_is_rejected():
    request = make_request()
    runtime = InProcessWorkingAgentRuntime({"agent-1": lambda inputs: {"ok": True}})
    coordinator = RuntimeCoordinator()
    coordinator.coordinate(request, runtime)

    try:
        coordinator.coordinate(request, runtime)
    except ValueError as exc:
        assert "already accepted" in str(exc)
    else:
        raise AssertionError("duplicate execution request was accepted")


def test_missing_agent_becomes_unresolved():
    request = make_request()
    record = RuntimeCoordinator().coordinate(request, InProcessWorkingAgentRuntime({}))

    assert record.state == "UNRESOLVED"
    assert record.outcome_status == "UNRESOLVED"
    assert record.escalation_information


def test_runtime_failure_is_preserved():
    request = make_request()

    def fail(_inputs):
        raise RuntimeError("boom")

    record = RuntimeCoordinator().coordinate(request, InProcessWorkingAgentRuntime({"agent-1": fail}))

    assert record.state == "FAILED"
    assert record.outcome_status == "FAILED"
    assert "RuntimeError" in record.failure_information[0]


def test_incomplete_request_is_rejected_before_runtime_submission():
    request = make_request()
    invalid = request.__class__(
        request_id=request.request_id,
        project_id=request.project_id,
        plan_decision_ref=request.plan_decision_ref,
        authorization_decision_ref=request.authorization_decision_ref,
        selected_route_ref=request.selected_route_ref,
        capability_ref=request.capability_ref,
        provider_type=request.provider_type,
        provider_ref="",
        inputs=request.inputs,
        authorized_scope=request.authorized_scope,
        provenance=request.provenance,
    )
    try:
        RuntimeCoordinator().coordinate(invalid, InProcessWorkingAgentRuntime({}))
    except ValueError as exc:
        assert "provider_ref" in str(exc)
    else:
        raise AssertionError("incomplete request was coordinated")


def test_coordinator_exposes_no_authorization_or_execution_api():
    coordinator = RuntimeCoordinator()
    assert not hasattr(coordinator, "authorize")
    assert not hasattr(coordinator, "execute")
    assert not hasattr(coordinator, "invoke")
    assert not hasattr(coordinator, "schedule")
    assert not hasattr(coordinator, "retry")
