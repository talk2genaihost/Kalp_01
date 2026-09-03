# Market Manthan — Architecture Baseline

## System flow

Provider Sources
→ Provider Adapter Framework (PAF)
→ Normalized + Validated + Quality-Aware Data
→ Manthan / Fusion
→ Decision-Ready Intelligence
→ Consultant Screen
→ User Feedback

## PAF
Provider-specific APIs and formats remain behind adapters. Responsibilities: acquisition, normalization, validation, retry/failover, provider health, freshness/quality metadata and confidence signals.

## Manthan / Fusion
Consumes validated provider data, combines relevant signals, detects contradictory evidence, adjusts confidence and produces structured intelligence while preserving uncertainty.

## Consultant Screen
Presentation and interaction layer. Expected fields: summary, supporting signals, conflicting signals, confidence, risk flags, suggested next action and feedback.

## Governance
Changes are versioned, traceable, reviewable and rollback-ready. Critical changes require explicit review/approval.

## Not yet specified
Exact providers, canonical schema, signal taxonomy, confidence formula, persistence, UI technology, authentication, deployment and any execution/trading behavior.
