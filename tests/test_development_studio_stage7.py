from development_studio.authorization_boundary import AuthorizationBoundary


def test_authorizes_with_explicit_scope():
    result = AuthorizationBoundary().authorize(
        plan_decision_ref="PLAN-1",
        selected_route_ref="R-1",
        authority_scope=["sap.analysis"],
        required_scope=["sap.analysis"],
        provenance=["route:R-1"],
    )
    assert result.result == "AUTHORIZED"
    assert result.authorized_scope == ("sap.analysis",)
    assert result.provenance == ("route:R-1",)


def test_denies_scope_excess():
    result = AuthorizationBoundary().authorize(
        plan_decision_ref="PLAN-2",
        selected_route_ref="R-1",
        authority_scope=["sap.analysis"],
        required_scope=["sap.analysis", "production.change"],
    )
    assert result.result == "DENIED"


def test_unresolved_without_selected_route():
    result = AuthorizationBoundary().authorize(
        plan_decision_ref="PLAN-3",
        selected_route_ref=None,
        authority_scope=["sap.analysis"],
    )
    assert result.result == "UNRESOLVED"
    assert result.escalation_requirements


def test_unresolved_without_explicit_authority():
    result = AuthorizationBoundary().authorize(
        plan_decision_ref="PLAN-4",
        selected_route_ref="R-1",
        authority_scope=[],
    )
    assert result.result == "UNRESOLVED"


def test_authority_conflict_escalates():
    result = AuthorizationBoundary().authorize(
        plan_decision_ref="PLAN-5",
        selected_route_ref="R-1",
        authority_scope=["sap.analysis"],
        authorization_context={"authority_conflict": True},
    )
    assert result.result == "UNRESOLVED"
    assert "authority review required" in result.escalation_requirements


def test_no_execution_or_invocation_api():
    boundary = AuthorizationBoundary()
    assert not hasattr(boundary, "execute")
    assert not hasattr(boundary, "invoke")
    assert not hasattr(boundary, "approve")
