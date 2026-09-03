"""Governed Tool/Model interaction seams for Development Studio.

Implementation boundary derived from retrieved KALP runtime architecture. This
module defines injectable gateway ports and a bounded dispatcher. It does not
implement credentials, provider SDKs, policy authority, or unrestricted
external execution.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol, Literal
from uuid import uuid4

ProviderKind = Literal["TOOL", "MODEL"]


@dataclass(frozen=True)
class CapabilityInvocation:
    invocation_id: str = field(default_factory=lambda: f"capinv_{uuid4().hex}")
    request_id: str = ""
    provider_kind: ProviderKind = "TOOL"
    capability_ref: str = ""
    provider_ref: str = ""
    inputs: Mapping[str, Any] = field(default_factory=dict)
    authorized_scope: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()
    provenance: tuple[str, ...] = ()


@dataclass(frozen=True)
class CapabilityObservation:
    request_id: str = ""
    status: str = "UNRESOLVED"
    outputs: Mapping[str, Any] = field(default_factory=dict)
    evidence_refs: tuple[str, ...] = ()
    failure_information: tuple[str, ...] = ()
    escalation_information: tuple[str, ...] = ()
    provenance: tuple[str, ...] = ()


class GovernedCapabilityGateway(Protocol):
    def invoke(self, invocation: CapabilityInvocation) -> CapabilityObservation: ...


class GovernedCapabilityDispatcher:
    """Send an already-authorized invocation to an injected governed gateway."""

    def dispatch(self, invocation: CapabilityInvocation, gateway: GovernedCapabilityGateway) -> CapabilityObservation:
        self._validate(invocation)
        observation = gateway.invoke(invocation)
        if observation.request_id != invocation.request_id:
            raise ValueError("gateway observation request identity does not match invocation")
        if observation.status not in {"SUCCEEDED", "FAILED", "UNRESOLVED", "ESCALATED"}:
            raise ValueError(f"unsupported gateway observation status: {observation.status}")
        return observation

    @staticmethod
    def _validate(invocation: CapabilityInvocation) -> None:
        required = {
            "request_id": invocation.request_id,
            "capability_ref": invocation.capability_ref,
            "provider_ref": invocation.provider_ref,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise ValueError(f"missing capability invocation metadata: {', '.join(missing)}")
        if not invocation.authorized_scope:
            raise ValueError("authorized_scope is required")
        if not invocation.provenance:
            raise ValueError("provenance is required")
