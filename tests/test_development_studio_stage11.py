from development_studio.execution_boundary import ExecutionBoundary
from development_studio.runtime_coordinator import RuntimeCoordinator
from development_studio.agent_runtime import InProcessWorkingAgentRuntime
from development_studio.checkpoint_recovery import CheckpointRecoveryBoundary
from development_studio.evidence_verification import EvidenceBundle, EvidenceVerificationBoundary, VerificationResult
from development_studio.governed_capability_gateway import CapabilityInvocation, GovernedCapabilityDispatcher, CapabilityObservation


def make_request():
    return ExecutionBoundary().create_request(
        project_id="p1", plan_decision_ref="plan-1", authorization_decision_ref="auth-1",
        authorization_result="AUTHORIZED", selected_route_ref="route-1", capability_ref="cap-1",
        provider_type="AGENT", provider_ref="agent-1", inputs={"x": 2},
        authorized_scope=("execute:task",), provenance=("stage11-test",),
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
    coordinator = RuntimeCoordinator(); coordinator.coordinate(request, runtime)
    try: coordinator.coordinate(request, runtime)
    except ValueError as exc: assert "already accepted" in str(exc)
    else: raise AssertionError("duplicate execution request was accepted")


def test_missing_agent_becomes_unresolved():
    record = RuntimeCoordinator().coordinate(make_request(), InProcessWorkingAgentRuntime({}))
    assert record.state == "UNRESOLVED" and record.outcome_status == "UNRESOLVED"
    assert record.escalation_information


def test_runtime_failure_is_preserved():
    def fail(_inputs): raise RuntimeError("boom")
    record = RuntimeCoordinator().coordinate(make_request(), InProcessWorkingAgentRuntime({"agent-1": fail}))
    assert record.state == "FAILED" and record.outcome_status == "FAILED"
    assert "RuntimeError" in record.failure_information[0]


def test_incomplete_request_is_rejected_before_runtime_submission():
    request = make_request()
    invalid = request.__class__(request_id=request.request_id, project_id=request.project_id,
        plan_decision_ref=request.plan_decision_ref, authorization_decision_ref=request.authorization_decision_ref,
        selected_route_ref=request.selected_route_ref, capability_ref=request.capability_ref,
        provider_type=request.provider_type, provider_ref="", inputs=request.inputs,
        authorized_scope=request.authorized_scope, provenance=request.provenance)
    try: RuntimeCoordinator().coordinate(invalid, InProcessWorkingAgentRuntime({}))
    except ValueError as exc: assert "provider_ref" in str(exc)
    else: raise AssertionError("incomplete request was coordinated")


def test_coordinator_exposes_no_authorization_or_execution_api():
    coordinator = RuntimeCoordinator()
    for name in ("authorize", "execute", "invoke", "schedule", "retry"):
        assert not hasattr(coordinator, name)


class Gateway:
    def invoke(self, invocation):
        return CapabilityObservation(request_id=invocation.request_id, status="SUCCEEDED", outputs={"ok": True}, provenance=invocation.provenance)


class Verifier:
    def verify(self, evidence):
        return VerificationResult(request_id=evidence.request_id, status="VERIFIED", evidence_refs=evidence.evidence_refs, provenance=evidence.provenance)


def test_governed_tool_or_model_gateway_preserves_identity_and_provenance():
    invocation = CapabilityInvocation(request_id="r1", provider_kind="TOOL", capability_ref="cap1", provider_ref="tool1", authorized_scope=("read",), provenance=("auth:a",))
    result = GovernedCapabilityDispatcher().dispatch(invocation, Gateway())
    assert result.request_id == "r1" and result.status == "SUCCEEDED" and result.provenance == ("auth:a",)


def test_gateway_requires_authorized_scope():
    invocation = CapabilityInvocation(request_id="r1", capability_ref="cap1", provider_ref="tool1", provenance=("auth:a",))
    try: GovernedCapabilityDispatcher().dispatch(invocation, Gateway())
    except ValueError as exc: assert "authorized_scope" in str(exc)
    else: raise AssertionError("missing authorization scope was accepted")


def test_evidence_verification_is_separate_and_evidence_based():
    evidence = EvidenceBundle(request_id="r1", execution_id="e1", evidence_refs=("source:1",), provenance=("exec:e1",))
    result = EvidenceVerificationBoundary().verify(evidence, Verifier())
    assert result.status == "VERIFIED" and result.evidence_refs == ("source:1",)


def test_checkpoint_recovery_requires_policy_revalidation():
    boundary = CheckpointRecoveryBoundary()
    checkpoint = boundary.create_checkpoint(request_id="r1", execution_id="e1", plan_ref="p1", state="EXECUTING", resumable_state={"step": 2}, provenance=("exec:e1",), integrity_ref="hash:1")
    attempt = boundary.recover(checkpoint, lambda _: False)
    assert attempt.status == "ESCALATED"


def test_checkpoint_recovery_creates_new_attempt():
    boundary = CheckpointRecoveryBoundary()
    checkpoint = boundary.create_checkpoint(request_id="r1", execution_id="e1", plan_ref="p1", state="EXECUTING", resumable_state={"step": 2}, provenance=("exec:e1",), integrity_ref="hash:1")
    attempt = boundary.recover(checkpoint, lambda _: True)
    assert attempt.status == "READY" and attempt.source_checkpoint_ref == checkpoint.checkpoint_id
    assert attempt.attempt_id != checkpoint.checkpoint_id


def test_new_seams_do_not_authorize_or_execute():
    assert not hasattr(GovernedCapabilityDispatcher, "authorize")
    assert not hasattr(GovernedCapabilityDispatcher, "execute")
    assert not hasattr(CheckpointRecoveryBoundary, "execute")
