"""Bounded in-process Working-Agent runtime reference implementation.

This is an implementation artifact derived from the retrieved KALP runtime
specification. It executes only an injected Working-Agent handler. It does
not provide credentials, tool/model gateways, scheduling, discovery, or
authorization.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping
from uuid import uuid4

from .working_agent_runtime import RuntimeOutcome, RuntimeSubmission

TERMINAL_STATES = {"COMPLETED", "FAILED", "CANCELLED", "TIMED_OUT", "BUDGET_EXCEEDED"}


@dataclass(frozen=True)
class RuntimeExecution:
    execution_id: str = field(default_factory=lambda: f"runtime_{uuid4().hex}")
    request_id: str = ""
    state: str = "CREATED"
    outputs: Mapping[str, Any] = field(default_factory=dict)
    evidence_refs: tuple[str, ...] = ()
    failure_information: tuple[str, ...] = ()
    escalation_information: tuple[str, ...] = ()
    provenance: tuple[str, ...] = ()
    state_history: tuple[str, ...] = ("CREATED",)


class InProcessWorkingAgentRuntime:
    """Minimal concrete runtime for a registered/injected Working-Agent handler."""

    def __init__(self, handlers: Mapping[str, Callable[[Mapping[str, Any]], Mapping[str, Any]]]):
        self._handlers = dict(handlers)

    def submit(self, submission: RuntimeSubmission) -> RuntimeOutcome:
        if submission.provider_type != "AGENT":
            return RuntimeOutcome(
                request_id=submission.request_id,
                runtime_state="FAILED",
                status="FAILED",
                failure_information=("InProcessWorkingAgentRuntime accepts AGENT providers only",),
                provenance=submission.provenance,
            )
        handler = self._handlers.get(submission.provider_ref)
        if handler is None:
            return RuntimeOutcome(
                request_id=submission.request_id,
                runtime_state="UNRESOLVED",
                status="UNRESOLVED",
                escalation_information=(f"no handler registered for agent: {submission.provider_ref}",),
                provenance=submission.provenance,
            )
        try:
            outputs = dict(handler(dict(submission.inputs)))
        except Exception as exc:
            return RuntimeOutcome(
                request_id=submission.request_id,
                runtime_state="FAILED",
                status="FAILED",
                failure_information=(f"working-agent handler failed: {type(exc).__name__}: {exc}",),
                provenance=submission.provenance,
            )
        return RuntimeOutcome(
            request_id=submission.request_id,
            runtime_state="COMPLETED",
            status="SUCCEEDED",
            outputs=outputs,
            provenance=submission.provenance,
        )

    def run(self, submission: RuntimeSubmission) -> RuntimeExecution:
        outcome = self.submit(submission)
        state = outcome.runtime_state or ("COMPLETED" if outcome.status == "SUCCEEDED" else "FAILED")
        return RuntimeExecution(
            request_id=submission.request_id,
            state=state,
            outputs=outcome.outputs,
            evidence_refs=outcome.evidence_refs,
            failure_information=outcome.failure_information,
            escalation_information=outcome.escalation_information,
            provenance=outcome.provenance,
            state_history=("CREATED", "INITIALIZING", "CONTEXT_READY", "PLANNING", "PLAN_VALIDATED", "EXECUTING", state),
        )
