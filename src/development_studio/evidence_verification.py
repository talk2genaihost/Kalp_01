"""Execution evidence and verification boundary.

The retrieved KALP architecture requires verification before final release and
requires material outputs to retain evidence/source references. This boundary
keeps verification separate from execution and accepts an injected verifier.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol
from uuid import uuid4


@dataclass(frozen=True)
class EvidenceBundle:
    evidence_id: str = field(default_factory=lambda: f"evidence_{uuid4().hex}")
    request_id: str = ""
    execution_id: str = ""
    outputs: Mapping[str, Any] = field(default_factory=dict)
    evidence_refs: tuple[str, ...] = ()
    provenance: tuple[str, ...] = ()


@dataclass(frozen=True)
class VerificationResult:
    verification_id: str = field(default_factory=lambda: f"verify_{uuid4().hex}")
    request_id: str = ""
    status: str = "UNRESOLVED"
    findings: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    provenance: tuple[str, ...] = ()


class EvidenceVerifier(Protocol):
    def verify(self, evidence: EvidenceBundle) -> VerificationResult: ...


class EvidenceVerificationBoundary:
    """Validate evidence metadata and delegate domain verification."""

    def verify(self, evidence: EvidenceBundle, verifier: EvidenceVerifier) -> VerificationResult:
        self._validate(evidence)
        result = verifier.verify(evidence)
        if result.request_id != evidence.request_id:
            raise ValueError("verification request identity does not match evidence")
        if result.status not in {"VERIFIED", "REJECTED", "UNRESOLVED", "ESCALATED"}:
            raise ValueError(f"unsupported verification status: {result.status}")
        return result

    @staticmethod
    def _validate(evidence: EvidenceBundle) -> None:
        if not evidence.request_id:
            raise ValueError("request_id is required")
        if not evidence.execution_id:
            raise ValueError("execution_id is required")
        if not evidence.provenance:
            raise ValueError("provenance is required")
