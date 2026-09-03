"""Bounded, declarative planner/router for Development Studio.

This module plans only. It does not authorize, invoke, execute, or mutate
capability/routing registries.
"""
from dataclasses import dataclass, field
from typing import Any, Mapping, Optional, Sequence
from uuid import uuid4


@dataclass(frozen=True)
class PlanDecision:
    decision_id: str = field(default_factory=lambda: f"plan_{uuid4().hex}")
    request_id: str = ""
    candidate_route_refs: tuple[str, ...] = ()
    selected_route_ref: Optional[str] = None
    unresolved_conditions: tuple[str, ...] = ()
    escalation_requirements: tuple[str, ...] = ()
    provenance: tuple[str, ...] = ()

    @property
    def resolved(self) -> bool:
        return self.selected_route_ref is not None and not self.unresolved_conditions


class PlannerRouter:
    """Evaluate explicit routing candidates without becoming an executor."""

    def plan(
        self,
        *,
        request_id: str,
        request_class: str,
        candidates: Sequence[Mapping[str, Any]],
        context: Optional[Mapping[str, Any]] = None,
        required_capability: Optional[str] = None,
    ) -> PlanDecision:
        if not request_id:
            raise ValueError("request_id is required")
        if not request_class:
            raise ValueError("request_class is required")

        request_context = dict(context or {})
        applicable = []
        all_refs = []
        provenance = []

        for candidate in candidates:
            route_id = candidate.get("route_id")
            if not route_id:
                continue
            all_refs.append(route_id)
            provenance.extend(candidate.get("provenance") or candidate.get("source_references") or [])

            if candidate.get("request_class") != request_class:
                continue
            capability_id = candidate.get("capability_id")
            if required_capability and capability_id and capability_id != required_capability:
                continue

            conditions = candidate.get("selection_conditions") or {}
            if not isinstance(conditions, Mapping):
                continue
            if all(request_context.get(key) == value for key, value in conditions.items()):
                applicable.append(candidate)

        unresolved: list[str] = []
        escalation: list[str] = []
        selected: Optional[str] = None

        if not applicable:
            unresolved.append("no routing candidate satisfies the explicit request context")
            escalation.append("routing review required")
        elif len(applicable) > 1:
            unresolved.append("multiple routing candidates satisfy the explicit request context")
            escalation.append("routing selection requires governed resolution")
        else:
            selected = applicable[0]["route_id"]
            escalation.extend(applicable[0].get("escalation_conditions") or [])

        # Preserve declared authority/escalation metadata; this component does
        # not adjudicate authority conflicts.
        if applicable:
            authority_scopes = [set(c.get("authority_scope") or []) for c in applicable]
            if any(scope == set() for scope in authority_scopes):
                pass

        return PlanDecision(
            request_id=request_id,
            candidate_route_refs=tuple(all_refs),
            selected_route_ref=selected,
            unresolved_conditions=tuple(unresolved),
            escalation_requirements=tuple(escalation),
            provenance=tuple(dict.fromkeys(str(item) for item in provenance)),
        )

    # Deliberately no authorize(), execute(), invoke(), or mutate() API.
