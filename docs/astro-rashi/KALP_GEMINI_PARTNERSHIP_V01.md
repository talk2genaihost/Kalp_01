# KALP Astro Rashi — Shared Gemini Partnership v0.1

## Status

Implemented on the feature branch as a first integration slice. This change does not create a new Gemini API key or expose a Gemini secret to Astro Rashi or GitHub Pages.

## Canonical path

```text
Astro Rashi
    |
    +--> astro-kundli
    |       |
    |       +--> Prokerala OAuth / Kundli provider
    |       |
    |       +--> normalized chart payload
    |
    +--> KALP Intelligence Gateway
            |
            +--> provider=gemini
                    |
                    +--> Gemini
                    |
                    +--> Hindi structured interpretation
```

## Security boundary

- `GEMINI_API_KEY` / `GOOGLE_API_KEY` remains server-side in `kalp-intelligence-gateway`.
- Astro Rashi calls the shared gateway; it does not call the Gemini API directly.
- The gateway is the same KALP intelligence boundary already used by AdManthan and the Market Manthan integration.
- Astro Rashi sends normalized provider output to the gateway and asks Gemini to interpret only supplied facts.

## Interpretation contract

The first slice asks Gemini for JSON containing:

```json
{
  "summary": "string",
  "strengths": ["string"],
  "cautions": ["string"],
  "focus": ["string"]
}
```

The prompt requires conversational Hindi, prohibits fabricated placements, and uses non-deterministic interpretive language.

## Scope boundary

This is an interpretation bridge, not a replacement for astronomical calculation. Prokerala remains the calculation/provider layer in the current Astro Rashi slice. Gemini interprets the returned chart facts.

## Verification boundary

Repository wiring has been implemented and the existing `build:astro-rashi` path remains the build target. A live Gemini round-trip from this environment is not claimed unless the deployed site is exercised with the required browser configuration and network access.
