"""Bounded integration of governed runtime seams.

This module composes existing Development Studio boundaries without becoming a
new authorization engine, provider gateway, scheduler, or recovery controller.
Provider execution, domain verification, and policy revalidation are injected.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence
from uuid import uuid4

from .agent_runtime import InProcessWorkingAgentRuntime
from .checkpoint_recovery import CheckpointRecoveryBoundary, ExecutionCheckpoint, RecoveryAttempt
from .evidence_verification import EvidenceBundle, EvidenceVerificationBoundary, EvidenceVerifier, VerificationResult
from .execution_boundary import ExecutionRequest
from .governed_capability_gateway import (
    CapabilityInvocation,
    CapabilityObservation,
    GovernedCapabilityDispatcher,
    GovernedCapabilityGateway,
)
from .working_agent_runtime import RuntimeOutcome


@dataclass(frozen=True)
class GovernedPipelineResult:
    pipeline_id: str = field(default_factory=lambda: f"pipeline_{uuid4().hex}")
    request_id: str = ""
    runtime_status: str = "UNRESOLVED"
    gateway_status: str = "NOT_REQUIRED"
    verification_status: str = "UNRESOLVED"
    recovery_status: str = "NOT_REQUIRED"
    outputs: Mapping[str, Any] = field(default_factory=dict)
    evidence_refs: tuple[str, ...] = ()
    provenance: tuple[str, ...] = ()
    findings: tuple[str, ...] = ()


class GovernedExecutionPipeline:
    """Compose runtime, gateway, verification and recovery boundaries."""

    def __init__(
        self,
        *,
        capability_gateway: GovernedCapabilityGateway | None = None,
        verifier: EvidenceVerifier | None = None,
        checkpoint_boundary: CheckpointRecoveryBoundary | None = None,
    ) -> None:
        self.capability_gateway = capability_gateway
        self.verifier = verifier
        self.checkpoint_boundary = checkpoint_boundary or CheckpointRecoveryBoundary()
        self._dispatcher = GovernedCapabilityDispatcher()
        self._verification = EvidenceVerificationBoundary()

    def process(
        self,
        request: ExecutionRequest,
        runtime: InProcessWorkingAgentRuntime,
        *,
        capability_invocation: CapabilityInvocation | None = None,
        checkpoint: ExecutionCheckpoint | None = None,
        revalidate_policy=None,
    ) -> GovernedPipelineResult:
        runtime_submission = self._to_submission(request)
        runtime_outcome: RuntimeOutcome = runtime.submit(runtime_submission)
        provenance = tuple(dict.fromkeys((*request.provenance, *runtime_outcome.provenance)))
        outputs = dict(runtime_outcome.outputs)
        evidence_refs = tuple(runtime_outcome.evidence_refs)
        gateway_status = "NOT_REQUIRED"

        if capability_invocation is not None:
            if self.capability_gateway is None:
                raise ValueError("capability gateway is required when capability_invocation is supplied")
            gateway_observation = self._dispatcher.dispatch(capability_invocation, self.capability_gateway)
            gateway_status = gateway_observation.status
            outputs.update(gateway_observation.outputs)
            evidence_refs = tuple(dict.fromkeys((*evidence_refs, *gateway_observation.evidence_refs)))
            provenance = tuple(dict.fromkeys((*provenance, *gateway_observation.provenance)))
            if gateway_observation.status != "SUCCEEDED":
                return GovernedPipelineResult(
                    request_id=request.request_id,
                    runtime_status=runtime_outcome.status,
                    gateway_status=gateway_status,
                    outputs=outputs,
                    evidence_refs=evidence_refs,
                    provenance=provenance,
                    findings=tuple(gateway_observation.failure_information) + tuple(gateway_observation.escalation_information),
                )

        verification_status = "NOT_REQUIRED"
        findings: list[str] = list(runtime_outcome.failure_information) + list(runtime_outcome.escalation_information)
        if self.verifier is not None:
            evidence = EvidenceBundle(
                request_id=request.request_id,
                execution_id=request.request_id,
                outputs=outputs,
                evidence_refs=evidence_refs,
                provenance=provenance,
            )
            verification = self._verification.verify(evidence, self.verifier)
            verification_status = verification.status
            evidence_refs = tuple(dict.fromkeys((*evidence_refs, *verification.evidence_refs)))
            provenance = tuple(dict.fromkeys((*provenance, *verification.provenance)))
            findings.extend(verification.findings)

        recovery_status = "NOT_REQUIRED"
        if checkpoint is not None:
            if revalidate_policy is None:
                raise ValueError("revalidate_policy is required when checkpoint recovery is requested")
            recovery: RecoveryAttempt = self.checkpoint_boundary.recover(checkpoint, revalidate_policy)
            recovery_status = recovery.status
            findings.extend(recovery.escalation_information)

        return GovernedPipelineResult(
            request_id=request.request_id,
            runtime_status=runtime_outcome.status,
            gateway_status=gateway_status,
            verification_status=verification_status,
            recovery_status=recovery_status,
            outputs=outputs,
            evidence_refs=evidence_refs,
            provenance=provenance,
            findings=tuple(findings),
        )

    @staticmethod
    def _to_submission(request: ExecutionRequest):
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
