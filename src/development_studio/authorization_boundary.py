"""Bounded authorization decision boundary for Development Studio."""
from dataclasses import dataclass, field
from typing import Mapping, Optional, Sequence
from uuid import uuid4


@dataclass(frozen=True)
class AuthorizationDecision:
    decision_id: str = field(default_factory=lambda: f"auth_{uuid4().hex}")
    plan_decision_ref: str = ""
    result: str = "UNRESOLVED"
    authorized_scope: tuple[str, ...] = ()
    unresolved_conditions: tuple[str, ...] = ()
    escalation_requirements: tuple[str, ...] = ()
    provenance: tuple[str, ...] = ()


class AuthorizationBoundary:
    """Evaluate an existing plan against explicit authority information."""

    def authorize(self, *, plan_decision_ref: str, selected_route_ref: Optional[str], authority_scope: Sequence[str], required_scope: Sequence[str] = (), provenance: Sequence[str] = (), escalation_conditions: Sequence[str] = (), authorization_context: Optional[Mapping[str, object]] = None) -> AuthorizationDecision:
        if not plan_decision_ref:
            raise ValueError("plan_decision_ref is required")
        declared = tuple(dict.fromkeys(str(x) for x in authority_scope))
        required = tuple(dict.fromkeys(str(x) for x in required_scope))
        provenance = tuple(dict.fromkeys(str(x) for x in provenance))
        escalation = tuple(dict.fromkeys(str(x) for x in escalation_conditions))
        context = dict(authorization_context or {})
        unresolved = []
        result = "UNRESOLVED"
        authorized = ()

        if not selected_route_ref:
            unresolved.append("selected route is required before authorization")
        elif not declared:
            unresolved.append("explicit authority scope is required")
        elif required and not set(required).issubset(set(declared)):
            result = "DENIED"
            unresolved.append("required scope exceeds declared authority scope")
        elif context.get("authority_conflict") is True:
            unresolved.append("authorization context declares an authority conflict")
            escalation = tuple(dict.fromkeys((*escalation, "authority review required")))
        else:
            result = "AUTHORIZED"
            authorized = declared

        if unresolved and result == "UNRESOLVED" and not escalation:
            escalation = ("authorization review required",)

        return AuthorizationDecision(plan_decision_ref=plan_decision_ref, result=result, authorized_scope=authorized, unresolved_conditions=tuple(unresolved), escalation_requirements=escalation, provenance=provenance)

    # Deliberately no execute(), invoke(), approve(), or registry mutation API.
