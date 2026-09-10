import os
from .openai_adapter import OpenAIProviderAdapter
def configured_providers(): return {"openai":OpenAIProviderAdapter()} if os.getenv("OPENAI_API_KEY") else {}
def provider_health():
    p=configured_providers(); return {"status":"READY","providers":{k:v.health() for k,v in p.items()}} if p else {"status":"NO_PROVIDER_CONFIGURED","providers":{}}
