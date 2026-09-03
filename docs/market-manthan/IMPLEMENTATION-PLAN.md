# Market Manthan — Implementation Plan v0.1

## 1. Confirmed requirements
1. Provider-specific market data is isolated behind PAF adapters.
2. PAF normalizes and validates provider data.
3. PAF exposes freshness, completeness, quality/confidence metadata and provider health.
4. Provider failure must be observable; retry/failover must not hide degradation.
5. Manthan/Fusion consumes validated data, combines signals and preserves contradictory evidence.
6. Intelligence output contains summary, supporting signals, conflicting signals, confidence, risk flags and suggested next action.
7. Consultant Screen presents intelligence rather than replacing the intelligence layer.
8. Feedback is captured as structured events and does not silently change rules.
9. Financial outputs remain informational/decision-support outputs unless explicit execution authority is separately specified.

## 2. Open questions
- Exact provider list and contracts
- Canonical market-data schema
- Production data sources and credentials/configuration model
- Signal taxonomy
- Confidence calculation formula
- Persistence/database design
- UI technology and authentication/user roles
- Deployment target
- Any future trading/execution requirements

## 3. Proposed module boundaries
- `paf.contracts`: provider-neutral interfaces and canonical records
- `paf.adapters`: provider-specific implementations
- `paf.normalization`: provider-to-canonical transformations
- `paf.validation`: schema/data-quality validation
- `paf.reliability`: retry, failover and health state
- `manthan.models`: signals, conflicts, confidence and intelligence objects
- `manthan.fusion`: deterministic signal combination and conflict handling
- `consultant_screen`: presentation/input contract only
- `feedback`: structured feedback events
- `governance`: versioning, traceability and review records

These are proposed implementation boundaries, not canonical contracts.

## 4. Interfaces/contracts to establish before broad implementation
- ProviderAdapter interface
- ProviderRegistry
- CanonicalMarketRecord
- Quality/Freshness metadata
- ProviderHealth
- FusionInput/FusionOutput
- Signal and Conflict records
- ConsultantScreenInput
- FeedbackEvent

Exact schemas remain TBD where the preparation package does not define them.

## 5. Test strategy
- Adapter contract compliance
- Normalization and validation
- Malformed/incomplete/stale data
- Provider failure, retry/failover and degraded health
- Conflicting signals
- Confidence propagation/adjustment
- Intelligence output schema
- Consultant Screen input contract
- Feedback event structure
- End-to-end degraded-data scenarios

No production credentials in source control.

## 6. Implementation order
1. Freeze/approve the provider-neutral contracts.
2. Build PAF core with a mock/reference provider only.
3. Add normalization, validation, quality/freshness and health behavior.
4. Add bounded retry/failover behavior.
5. Build Manthan/Fusion deterministic models and conflict handling.
6. Build Consultant Screen input contract and a minimal screen.
7. Add structured feedback.
8. Integrate end-to-end and test degraded scenarios.
9. Only then assess production providers, deployment and release readiness.

## First demonstrable target
**Market Manthan Watchlist Flash:** a small consultant-style view of five explicitly configured symbols using a mock/reference provider until a real provider contract is approved. It must expose data quality/confidence and conflicts rather than hiding them.
