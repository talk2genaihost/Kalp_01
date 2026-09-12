from gini.generation.providers.registry import provider_health

def test_provider_layer_is_credential_safe():
    h = provider_health()
    assert "providers" in h
    assert "OPENAI_API_KEY" not in str(h)
