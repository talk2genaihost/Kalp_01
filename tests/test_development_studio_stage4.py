import pytest

from src.development_studio.capability_registry import Capability, CapabilityRegistry
from src.development_studio.persistence.sqlite import SQLiteStore


def make_registry():
    return CapabilityRegistry(SQLiteStore())


def make_capability(**overrides):
    values = {
        "name": "requirements-analysis",
        "version": "1.0",
        "description": "Analyze structured requirements.",
        "provider_type": "AGENT",
        "provider_ref": "agent.requirements",
        "required_inputs": {"requirements": "object"},
        "expected_outputs": {"analysis": "object"},
        "constraints": ["read-only"],
        "authority_scope": ["development-studio"],
        "escalation_conditions": ["missing requirements"],
        "status": "AVAILABLE",
        "provenance": ["source:requirements-contract"],
    }
    values.update(overrides)
    return Capability(**values)


def test_register_and_retrieve_preserves_contract_metadata():
    registry = make_registry()
    capability = make_capability(capability_id="cap_analysis_v1")

    registry.register(capability)
    record = registry.get(capability.capability_id)

    assert record["provider_type"] == "AGENT"
    assert record["provider_ref"] == "agent.requirements"
    assert record["required_inputs"] == {"requirements": "object"}
    assert record["expected_outputs"] == {"analysis": "object"}
    assert record["constraints"] == ["read-only"]
    assert record["authority_scope"] == ["development-studio"]
    assert record["escalation_conditions"] == ["missing requirements"]
    assert record["provenance"] == ["source:requirements-contract"]


def test_registry_lists_by_lifecycle_status():
    registry = make_registry()
    registry.register(make_capability(capability_id="cap_a", status="AVAILABLE"))
    registry.register(make_capability(capability_id="cap_b", status="DISCOVERED"))

    assert [item["id"] for item in registry.list("AVAILABLE")] == ["cap_a"]


def test_duplicate_capability_identity_is_rejected():
    registry = make_registry()
    registry.register(make_capability(capability_id="cap_same"))

    with pytest.raises(ValueError, match="capability already exists"):
        registry.register(make_capability(capability_id="cap_same"))


def test_invalid_provider_type_is_rejected():
    registry = make_registry()

    with pytest.raises(ValueError, match="provider_type"):
        registry.register(make_capability(provider_type="RUNTIME"))


def test_missing_required_metadata_is_rejected_without_persistence():
    registry = make_registry()
    capability = make_capability(capability_id="cap_invalid", provider_ref="")

    with pytest.raises(ValueError, match="provider_ref"):
        registry.register(capability)

    assert registry.get("cap_invalid") is None


def test_discovery_does_not_grant_execution_authority():
    registry = make_registry()
    registry.register(make_capability(capability_id="cap_discovered", status="DISCOVERED"))

    record = registry.get("cap_discovered")
    assert record["status"] == "DISCOVERED"
    assert "authorize" not in record
    assert "execution_granted" not in record
