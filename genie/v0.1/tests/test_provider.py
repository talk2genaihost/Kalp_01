from gini.generation.providers.registry import provider_health
def test_provider_health_does_not_expose_credentials():
    h=provider_health(); assert "OPENAI_API_KEY" not in str(h)
