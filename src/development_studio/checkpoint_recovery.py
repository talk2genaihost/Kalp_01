"""Bounded checkpoint and recovery seam for Development Studio.

Recovery creates a new attempt from a validated checkpoint. It never mutates
prior attempts, silently changes a plan, or stores secrets in checkpoint data.
Policy revalidation is delegated to an injected callback before resume.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping
from uuid import uuid4


@dataclass(frozen=True)
class ExecutionCheckpoint:
    checkpoint_id: str = field(default_factory=lambda: f"ckpt_{uuid4().hex}")
    request_id: str = ""
    execution_id: str = ""
    plan_ref: str = ""
    state: str = ""
    resumable_state: Mapping[str, Any] = field(default_factory=dict)
    provenance: tuple[str, ...] = ()
    integrity_ref: str = ""


@dataclass(frozen=True)
class RecoveryAttempt:
    attempt_id: str = field(default_factory=lambda: f"attempt_{uuid4().hex}")
    request_id: str = ""
    source_checkpoint_ref: str = ""
    plan_ref: str = ""
    status: str = "UNRESOLVED"
    resumable_state: Mapping[str, Any] = field(default_factory=dict)
    escalation_information: tuple[str, ...] = ()
    provenance: tuple[str, ...] = ()


class CheckpointRecoveryBoundary:
    """Create immutable checkpoints and safe new recovery attempts."""

    def create_checkpoint(self, *, request_id: str, execution_id: str, plan_ref: str,
                          state: str, resumable_state: Mapping[str, Any],
                          provenance: tuple[str, ...], integrity_ref: str) -> ExecutionCheckpoint:
        if not all((request_id, execution_id, plan_ref, state, integrity_ref)):
            raise ValueError("request_id, execution_id, plan_ref, state and integrity_ref are required")
        if not provenance:
            raise ValueError("provenance is required")
        return ExecutionCheckpoint(
            request_id=request_id, execution_id=execution_id, plan_ref=plan_ref,
            state=state, resumable_state=dict(resumable_state),
            provenance=tuple(provenance), integrity_ref=integrity_ref,
        )

    def recover(self, checkpoint: ExecutionCheckpoint,
                revalidate_policy: Callable[[ExecutionCheckpoint], bool]) -> RecoveryAttempt:
        if not checkpoint.request_id or not checkpoint.plan_ref or not checkpoint.integrity_ref:
            raise ValueError("checkpoint is not resumable")
        if not revalidate_policy(checkpoint):
            return RecoveryAttempt(
                request_id=checkpoint.request_id,
                source_checkpoint_ref=checkpoint.checkpoint_id,
                plan_ref=checkpoint.plan_ref,
                status="ESCALATED",
                escalation_information=("checkpoint resume failed policy revalidation",),
                provenance=checkpoint.provenance,
            )
        return RecoveryAttempt(
            request_id=checkpoint.request_id,
            source_checkpoint_ref=checkpoint.checkpoint_id,
            plan_ref=checkpoint.plan_ref,
            status="READY",
            resumable_state=dict(checkpoint.resumable_state),
            provenance=checkpoint.provenance,
        )
