from development_studio.agent_runtime import InProcessWorkingAgentRuntime
from development_studio.working_agent_runtime import RuntimeSubmission


def submission(provider_ref="agent-demo"):
    return RuntimeSubmission(
        request_id="exec-1",
        agent_ref=provider_ref,
        capability_ref="cap-1",
        provider_type="AGENT",
        provider_ref=provider_ref,
        inputs={"value": 4},
        authorized_scope=("analysis",),
        constraints=("bounded",),
        provenance=("stage9",),
    )


def test_working_agent_executes_injected_handler():
    runtime = InProcessWorkingAgentRuntime({"agent-demo": lambda inputs: {"result": inputs["value"] * 2}})
    outcome = runtime.submit(submission())
    assert outcome.status == "SUCCEEDED"
    assert outcome.runtime_state == "COMPLETED"
    assert outcome.outputs == {"result": 8}
    assert outcome.request_id == "exec-1"


def test_missing_agent_is_unresolved_not_fallback():
    outcome = InProcessWorkingAgentRuntime({}).submit(submission())
    assert outcome.status == "UNRESOLVED"
    assert outcome.runtime_state == "UNRESOLVED"
    assert "no handler registered" in outcome.escalation_information[0]


def test_handler_failure_is_failed():
    def broken(_):
        raise RuntimeError("boom")

    outcome = InProcessWorkingAgentRuntime({"agent-demo": broken}).submit(submission())
    assert outcome.status == "FAILED"
    assert outcome.runtime_state == "FAILED"
    assert "RuntimeError" in outcome.failure_information[0]


def test_tool_provider_is_not_executed_by_working_agent_runtime():
    request = submission()
    request = RuntimeSubmission(
        request_id=request.request_id,
        agent_ref="",
        capability_ref=request.capability_ref,
        provider_type="TOOL",
        provider_ref="tool-1",
        inputs=request.inputs,
        authorized_scope=request.authorized_scope,
        constraints=request.constraints,
        provenance=request.provenance,
    )
    outcome = InProcessWorkingAgentRuntime({"tool-1": lambda _: {"unsafe": True}}).submit(request)
    assert outcome.status == "FAILED"
    assert outcome.outputs == {}
