from development_studio.execution_boundary import ExecutionBoundary
from development_studio.agent_runtime import InProcessWorkingAgentRuntime
from development_studio.governed_capability_gateway import CapabilityInvocation
from development_studio.governed_execution_pipeline import GovernedExecutionPipeline


class Gateway:
    def invoke(self, invocation):
        from development_studio.governed_capability_gateway import CapabilityObservation
        return CapabilityObservation(
            request_id=invocation.request_id,
            status="SUCCEEDED",
            outputs={"tool_result": 5},
            evidence_refs=("tool-evidence-1",),
            provenance=("gateway-test",),
        )


class Verifier:
    def verify(self, evidence):
        from development_studio.evidence_verification import VerificationResult
        return VerificationResult(
            request_id=evidence.request_id,
            status="VERIFIED",
            findings=("output checked",),
            evidence_refs=("verification-1",),
            provenance=("verifier-test",),
        )


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
        provenance=("stage12-test",),
    )


def test_pipeline_composes_agent_gateway_and_verification():
    request = make_request()
    runtime = InProcessWorkingAgentRuntime({"agent-1": lambda inputs: {"agent_result": inputs["x"]}})
    invocation = CapabilityInvocation(
        request_id=request.request_id,
        provider_kind="TOOL",
        capability_ref="cap-1",
        provider_ref="tool-1",
        inputs={"value": 5},
        authorized_scope=request.authorized_scope,
        provenance=request.provenance,
    )
    result = GovernedExecutionPipeline(capability_gateway=Gateway(), verifier=Verifier()).process(
        request, runtime, capability_invocation=invocation
    )
    assert result.runtime_status == "SUCCEEDED"
    assert result.gateway_status == "SUCCEEDED"
    assert result.verification_status == "VERIFIED"
    assert result.outputs == {"agent_result": 2, "tool_result": 5}
    assert "tool-evidence-1" in result.evidence_refs
    assert "verification-1" in result.evidence_refs
    assert "gateway-test" in result.provenance
    assert "verifier-test" in result.provenance


def test_pipeline_does_not_require_gateway_when_no_capability_invocation():
    request = make_request()
    runtime = InProcessWorkingAgentRuntime({"agent-1": lambda inputs: {"ok": True}})
    result = GovernedExecutionPipeline().process(request, runtime)
    assert result.runtime_status == "SUCCEEDED"
    assert result.gateway_status == "NOT_REQUIRED"
    assert result.verification_status == "NOT_REQUIRED"


def test_pipeline_requires_policy_revalidation_for_recovery():
    request = make_request()
    runtime = InProcessWorkingAgentRuntime({"agent-1": lambda inputs: {"ok": True}})
    checkpoint = GovernedExecutionPipeline().checkpoint_boundary.create_checkpoint(
        request_id=request.request_id,
        execution_id="execution-1",
        plan_ref=request.plan_decision_ref,
        state="EXECUTING",
        resumable_state={"step": 1},
        provenance=request.provenance,
        integrity_ref="hash-1",
    )
    result = GovernedExecutionPipeline().process(
        request, runtime, checkpoint=checkpoint, revalidate_policy=lambda _: True
    )
    assert result.recovery_status == "READY"


def test_pipeline_preserves_failed_gateway_outcome():
    class FailedGateway:
        def invoke(self, invocation):
            from development_studio.governed_capability_gateway import CapabilityObservation
            return CapabilityObservation(
                request_id=invocation.request_id,
                status="FAILED",
                failure_information=("provider failed",),
                provenance=("failed-gateway",),
            )

    request = make_request()
    runtime = InProcessWorkingAgentRuntime({"agent-1": lambda inputs: {"ok": True}})
    invocation = CapabilityInvocation(
        request_id=request.request_id,
        provider_kind="MODEL",
        capability_ref="cap-1",
        provider_ref="model-1",
        inputs={},
        authorized_scope=request.authorized_scope,
        provenance=request.provenance,
    )
    result = GovernedExecutionPipeline(capability_gateway=FailedGateway()).process(
        request, runtime, capability_invocation=invocation
    )
    assert result.gateway_status == "FAILED"
    assert "provider failed" in result.findings
    assert result.verification_status == "NOT_REQUIRED"
