# KALP Astro Rashi — Prokerala Integration Specification

## Status

Phase 1 preparation. This document contains no credentials and does not claim that a live API request has been tested.

## Architecture

```text
Astro Rashi frontend (GitHub Pages)
        |
        v
KALP secure backend
        |
        +--> OAuth token service
        |
        +--> Prokerala Kundli adapter
        |
        v
KALP normalized chart model
        |
        v
Astro Rashi presentation and interpretation layer
```

## Security requirements

- The Prokerala Client Secret must never be placed in frontend JavaScript, HTML, public configuration, or GitHub Pages.
- Store `PROKERALA_CLIENT_ID` and `PROKERALA_CLIENT_SECRET` as backend deployment secrets.
- Do not log credentials or access tokens.
- Cache the access token until expiry; do not request a token for every frontend action.
- Return sanitized errors to the browser.

## Provider authentication

The backend will use the OAuth 2.0 client-credentials flow documented by Prokerala:

1. Read credentials from secure environment variables.
2. Request an access token from the documented Prokerala token endpoint.
3. Cache the token for its documented validity period.
4. Attach the token to the Kundli request.
5. Refresh the token after expiry or an authentication failure.

## KALP internal request model

```json
{
  "birthDate": "YYYY-MM-DD",
  "birthTime": "HH:mm:ss",
  "timezone": "IANA timezone",
  "latitude": 0.0,
  "longitude": 0.0,
  "ayanamsa": "lahiri"
}
```

The adapter converts this internal model to the exact Prokerala request format. The frontend must not depend on provider-specific parameter names.

## First provider operation

The first operation is the documented Kundli endpoint:

```text
GET /v2/astrology/kundli
```

The adapter will send the documented `ayanamsa`, `coordinates`, and `datetime` parameters after validating the internal request.

## Normalized response model

The following is the KALP contract. Values are populated only after a successful provider response; no chart values are fabricated.

```json
{
  "status": "SUCCESS",
  "provider": "prokerala",
  "calculationSystem": "vedic",
  "ayanamsa": "lahiri",
  "birthDetails": {
    "date": "YYYY-MM-DD",
    "time": "HH:mm:ss",
    "timezone": "IANA timezone",
    "latitude": 0.0,
    "longitude": 0.0
  },
  "chart": {
    "lagna": null,
    "moonSign": null,
    "sunSign": null,
    "nakshatra": null,
    "planets": [],
    "houses": []
  },
  "metadata": {
    "provider": "prokerala",
    "sourceStatus": "PROVIDER"
  }
}
```

## Error contract

```text
INVALID_BIRTH_DETAILS
INVALID_LOCATION
PROVIDER_AUTH_FAILED
PROVIDER_RATE_LIMITED
PROVIDER_QUOTA_EXCEEDED
PROVIDER_UNAVAILABLE
PROVIDER_RESPONSE_INVALID
CALCULATION_UNAVAILABLE
```

The browser receives a safe user-facing message and a non-sensitive error code. Raw provider credentials, tokens, and internal request details are never returned.

## Phase 1 scope

- Birth date, time, and location input
- Latitude, longitude, and timezone handling
- Basic Kundli request
- Lagna, Moon sign, Sun sign, Nakshatra, planetary positions, and houses when supplied by the provider response
- Hindi and English presentation support
- Loading, success, and failure states
- Provider attribution where required by the selected plan

## Deferred scope

- Full dasha interpretation
- Advanced divisional charts
- Yoga and dosha engine
- AI-generated predictive interpretation
- Multi-provider fallback
- KALP-owned astronomical calculation engine

## Implementation sequence

1. Create a secure backend service.
2. Configure credentials through deployment secrets.
3. Implement token acquisition and caching.
4. Implement the Prokerala adapter.
5. Test one known birth profile.
6. Validate and normalize the response.
7. Add automated error handling.
8. Connect Astro Rashi to the backend.
9. Remove the demo calculation path only after live validation succeeds.

## Future migration

The frontend and interpretation layer will call the KALP normalized chart contract rather than Prokerala directly. A future KALP engine can therefore replace the Prokerala adapter without redesigning the Astro Rashi UI.
