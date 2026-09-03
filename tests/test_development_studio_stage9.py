from development_studio.execution_boundary import ExecutionRequest
from development_studio.working_agent_runtime import (
    RuntimeOutcome,
    RuntimeSubmission,
    WorkingAgentRuntimeBoundary,
)


class FakeGovernedRuntime:
    def __init__(self, outcome):
        self.outcome = outcome
        self.submissions = []

    def submit(self, submission: RuntimeSubmission) -> RuntimeOutcome:
        self.submissions.append(submission)
        return self.outcome


def make_request(**overrides):
    values = dict(
        request_id="exec-1",
        project_id="project-1",
        plan_decision_ref="plan-1",
        authorization_decision_ref="auth-1",
        selected_route_ref="route-1",
        capability_ref="cap-1",
        provider_type="AGENT",
        provider_ref="agent-1",
        inputs={"task": "demo"},
        authorized_scope=("analysis",),
        constraints=("bounded",),
        provenance=("stage8",),
    )
    values.update(overrides)
    return ExecutionRequest(**values)


def test_prepare_preserves_execution_governance_metadata():
    submission = WorkingAgentRuntimeBoundary().prepare(make_request())
    assert submission.request_id == "exec-1"
    assert submission.agent_ref == "agent-1"
    assert submission.capability_ref == "cap-1"
    assert submission.authorized_scope == ("analysis",)
    assert submission.constraints == ("bounded",)
    assert submission.provenance == ("stage8",)


def test_submit_uses_injected_runtime_and_maps_result():
    runtime = FakeGovernedRuntime(
        RuntimeOutcome(
            request_id="exec-1",
            runtime_state="COMPLETED",
            status="SUCCEEDED",
            outputs={"answer": "done"},
            evidence_refs=("evidence-1",),
            provenance=("runtime",),
        )
    )
    result = WorkingAgentRuntimeBoundary().submit(make_request(), runtime)
    assert result.status == "SUCCEEDED"
    assert result.outputs == {"answer": "done"}
    assert result.evidence_refs == ("evidence-1",)
    assert result.provenance == ("stage8", "runtime")
    assert len(runtime.submissions) == 1


def test_runtime_result_request_mismatch_is_rejected():
    runtime = FakeGovernedRuntime(RuntimeOutcome(request_id="other", status="SUCCEEDED"))
    try:
        WorkingAgentRuntimeBoundary().submit(make_request(), runtime)
    except ValueError as exc:
        assert "request_id" in str(exc)
    else:
        raise AssertionError("mismatched runtime result must be rejected")


def test_runtime_invalid_status_is_rejected():
    runtime = FakeGovernedRuntime(RuntimeOutcome(request_id="exec-1", status="INVALID"))
    try:
        WorkingAgentRuntimeBoundary().submit(make_request(), runtime)
    except ValueError as exc:
        assert "invalid result status" in str(exc)
    else:
        raise AssertionError("invalid runtime status must be rejected")


def test_missing_authorized_scope_is_rejected():
    request = make_request(authorized_scope=())
    try:
        WorkingAgentRuntimeBoundary().prepare(request)
    except ValueError as exc:
        assert "authorized_scope" in str(exc)
    else:
        raise AssertionError("missing authorization scope must be rejected")


def test_boundary_does_not_expose_runtime_control_methods():
    boundary = WorkingAgentRuntimeBoundary()
    for name in ("authorize", "schedule", "execute", "invoke", "retry", "cancel"):
        assert not hasattr(boundary, name)
