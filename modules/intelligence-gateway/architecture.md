# Phase 1 Architecture

```text
ONE-LINE USER INTENT
        |
        v
KALP APPLICATION
        |
        v
KALP INTELLIGENCE GATEWAY
        |
        +--> Intent / Context
        +--> Research request
        +--> Evidence / Context Pack
        +--> Model routing
        |       +--> Gemini FREE (primary)
        |       +--> OpenRouter FREE (fallback)
        |       +--> Groq FREE (fast fallback)
        |
        v
Structured intelligence response
        |
        +--> AdManthan
        +--> MarketManthan
        +--> KALP News
        +--> Genie
        +--> Future KALP applications
```

## Separation of concerns

Research retrieval produces evidence and context. The reasoning provider interprets that context and produces structured intelligence. Applications then apply their own domain-specific engines.

No provider is exposed directly to browser clients. API credentials are server-side secrets.
