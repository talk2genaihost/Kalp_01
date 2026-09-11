# KALP AdManthan v0.1 — Four-Stage Working Package

This package implements the four-stage working architecture defined in the project conversation.

## Stage 1 — AdManthan Core
- Imports the supplied Effect/Shortcut Excel library.
- Preserves all library shortcut names and metadata.
- Performs scene-specific keyword lookup.
- Generates a 15-second / 6-scene continuous-VO package.
- Marks effect matches as VERIFIED LIBRARY MATCH; missing required matches as NOT FOUND IN CURRENT EFFECT LIBRARY.

## Stage 2 — AdManthan Studio
- Minimal local web studio.
- Enter brand/product and generate the six-frame production view.
- Run: `python studio/server.py`, then open `http://127.0.0.1:8765`.

## Stage 3 — Production Bridge
- Provider-neutral job and manifest contracts.
- Does not pretend to be a video/image/audio provider.
- Ready for provider adapters to be attached.

## Stage 4 — KALP / Genie Integration
- Adapter wraps an AdManthan package as a KALP Genie Creative Engine handoff.
- Keeps AdManthan as an advertising-specific module rather than replacing Genie.

## Source / governance status
The AdManthan four-stage architecture is a DERIVED working implementation from the project conversation, not a promoted canonical KALP architecture source. The uploaded KALP governance sources require inferred architecture to remain distinct from canonical state and prohibit unsupported promotion.
