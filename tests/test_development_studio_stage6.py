import inspect

import pytest

from development_studio.planner_router import PlanDecision, PlannerRouter


def route(route_id, **overrides):
    value = {
        "route_id": route_id,
        "request_class": "sap_incident",
        "capability_id": "cap.sap",
        "department_ref": "dept.sap",
        "agent_ref": "agent.sap",
        "selection_conditions": {"severity": "high"},
        "authority_scope": ["sap.incident"],
        "escalation_conditions": ["escalate_if_blocked"],
        "provenance": [f"source:{route_id}"],
    }
    value.update(overrides)
    return value


def test_unique_explicit_match_selects_route():
    decision = PlannerRouter().plan(
        request_id="REQ-1",
        request_class="sap_incident",
        candidates=[route("route-1")],
        context={"severity": "high"},
        required_capability="cap.sap",
    )
    assert isinstance(decision, PlanDecision)
    assert decision.selected_route_ref == "route-1"
    assert decision.resolved


def test_multiple_matches_remain_unresolved():
    decision = PlannerRouter().plan(
        request_id="REQ-2",
        request_class="sap_incident",
        candidates=[route("route-1"), route("route-2")],
        context={"severity": "high"},
    )
    assert decision.selected_route_ref is None
    assert "multiple" in decision.unresolved_conditions[0]
    assert "route-1" in decision.candidate_route_refs
    assert "route-2" in decision.candidate_route_refs


def test_no_candidate_is_unresolved_without_fabrication():
    decision = PlannerRouter().plan(
        request_id="REQ-3",
        request_class="sap_incident",
        candidates=[route("route-1")],
        context={"severity": "low"},
    )
    assert decision.selected_route_ref is None
    assert decision.escalation_requirements


def test_provenance_and_escalation_are_preserved():
    decision = PlannerRouter().plan(
        request_id="REQ-4",
        request_class="sap_incident",
        candidates=[route("route-1")],
        context={"severity": "high"},
    )
    assert "source:route-1" in decision.provenance
    assert "escalate_if_blocked" in decision.escalation_requirements


def test_capability_mismatch_does_not_get_selected():
    decision = PlannerRouter().plan(
        request_id="REQ-5",
        request_class="sap_incident",
        candidates=[route("route-1", capability_id="cap.other")],
        context={"severity": "high"},
        required_capability="cap.sap",
    )
    assert decision.selected_route_ref is None


def test_no_execution_or_authorization_api():
    public = [name for name, value in inspect.getmembers(PlannerRouter, inspect.isfunction) if not name.startswith("_")]
    assert public == ["plan"]
    assert not hasattr(PlannerRouter, "execute")
    assert not hasattr(PlannerRouter, "authorize")
    assert not hasattr(PlannerRouter, "invoke")


def test_required_request_fields_are_not_invented():
    with pytest.raises(ValueError):
        PlannerRouter().plan(request_id="", request_class="x", candidates=[])
    with pytest.raises(ValueError):
        PlannerRouter().plan(request_id="REQ", request_class="", candidates=[])
