import pytest

from src.development_studio.persistence.sqlite import SQLiteStore
from src.development_studio.routing_registry import RoutingEntry, RoutingRegistry


def test_register_and_retrieve_preserves_routing_metadata():
    store = SQLiteStore()
    registry = RoutingRegistry(store)
    entry = RoutingEntry(
        route_id="route_research_001",
        request_class="research",
        version="0.1",
        capability_id="cap_research",
        department_ref="dept_research",
        agent_ref="agent_research_01",
        selection_conditions={"domain": "research", "mode": "single-domain"},
        authority_scope=["research"],
        escalation_conditions=["authority_conflict", "missing_context"],
        provenance=["ORCH-DEPENDENCY-001"],
    )
    registry.register(entry)
    record = registry.get(entry.route_id)
    assert record is not None
    assert record["capability_id"] == "cap_research"
    assert record["department_ref"] == "dept_research"
    assert record["agent_ref"] == "agent_research_01"
    assert record["selection_conditions"]["mode"] == "single-domain"
    assert record["authority_scope"] == ["research"]
    assert record["provenance"] == ["ORCH-DEPENDENCY-001"]


def test_multiple_candidates_are_preserved_without_silent_selection():
    store = SQLiteStore()
    registry = RoutingRegistry(store)
    for route_id, agent_ref in (("route_1", "agent_1"), ("route_2", "agent_2")):
        registry.register(
            RoutingEntry(
                route_id=route_id,
                request_class="creative",
                version="0.1",
                capability_id="cap_story",
                agent_ref=agent_ref,
                selection_conditions={},
                provenance=["VW-REGISTRY-001"],
            )
        )
    routes = registry.list(request_class="creative", capability_id="cap_story")
    assert [route["agent_ref"] for route in routes] == ["agent_1", "agent_2"]


def test_duplicate_route_identity_is_rejected():
    store = SQLiteStore()
    registry = RoutingRegistry(store)
    entry = RoutingEntry(
        route_id="route_duplicate",
        request_class="analysis",
        version="0.1",
        agent_ref="agent_1",
        selection_conditions={},
        provenance=["source"],
    )
    registry.register(entry)
    with pytest.raises(ValueError, match="duplicate route_id"):
        registry.register(entry)


def test_incomplete_route_is_rejected_without_persistence():
    store = SQLiteStore()
    registry = RoutingRegistry(store)
    entry = RoutingEntry(
        route_id="route_invalid",
        request_class="analysis",
        version="0.1",
        selection_conditions={},
        provenance=["source"],
    )
    with pytest.raises(ValueError, match="at least one"):
        registry.register(entry)
    assert registry.get("route_invalid") is None


def test_missing_provenance_is_rejected():
    store = SQLiteStore()
    registry = RoutingRegistry(store)
    entry = RoutingEntry(
        route_id="route_no_provenance",
        request_class="analysis",
        version="0.1",
        agent_ref="agent_1",
        selection_conditions={},
    )
    with pytest.raises(ValueError, match="provenance"):
        registry.register(entry)
    assert registry.get("route_no_provenance") is None


def test_routing_registry_has_no_execution_authority_api():
    registry = RoutingRegistry(SQLiteStore())
    assert not hasattr(registry, "execute")
    assert not hasattr(registry, "authorize")
    assert not hasattr(registry, "invoke")
