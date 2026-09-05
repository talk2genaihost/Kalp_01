# Astro Rashi Dashboard — Implementation Plan v0.1

## 1. Registration

- Project ID: `KALP-PROJ-ASTRO-RASHI-001`
- Parent system: KALP Development Studio
- Status: APPROVED FOR IMPLEMENTATION PLANNING
- Requirements: approved
- Architecture/UX: approved
- Implementation status: NOT_STARTED
- Platform: web-first, Android-ready
- Initial locales: `hi-IN`, `en-IN`

## 2. Implementation objective

Deliver a testable web MVP that demonstrates the approved dashboard and assistant workflows while preserving clear boundaries for future astrology calculation providers, multilingual content, privacy, and Android reuse.

## 3. Delivery strategy

### Phase 1 — Foundation

- Establish application shell and responsive layout.
- Add route/navigation structure for Dashboard, My Rashi, Assistant, Language, and Privacy/Settings.
- Add typed domain models and service interfaces.
- Add locale resource structure for Hindi and English.
- Add deterministic validation and error-state components.

### Phase 2 — Weekly rashi dashboard

- Implement stable identifiers for all 12 राशियाँ.
- Build responsive rashi card grid/list.
- Add weekly period selector/display.
- Add demo horoscope content with source, language, period, and publication status metadata.
- Add detailed rashi view.
- Add explicit demo/general-guidance labelling.

### Phase 3 — Birth-data and assistant workflow

- Implement date, place, time, and timezone fields.
- Validate required fields and invalid dates/times.
- Add privacy notice and reset/delete controls.
- Implement assistant question input and suggested questions.
- Implement answer types: general guidance, calculated output, interpretation, and unavailable.
- Ensure sensitive birth data is excluded from ordinary logs.

### Phase 4 — Calculation and content boundaries

- Define calculation-provider interface.
- Define content-provider interface.
- Define provenance model and source-reference propagation.
- Add placeholder adapters only; do not claim production calculations.
- Record unresolved decisions for tradition, ephemeris, ayanamsa, house system, timezone handling, and content authority.

### Phase 5 — Quality and release preparation

- Unit tests for localization, fallback, and validation.
- Component tests for all 12 rashi cards in both locales.
- Accessibility tests for navigation, forms, and errors.
- Privacy tests for log redaction and reset behavior.
- Integration tests for provenance propagation.
- Build and test evidence recorded in Development Studio.

## 4. Proposed module structure

```text
src/
  app/
    routes/
    shell/
  domain/
    rashi/
    horoscope/
    birth-profile/
    assistant/
    provenance/
  application/
    dashboard-service/
    assistant-service/
    validation-service/
  localization/
    hi-IN/
    en-IN/
    locale-resolver/
  adapters/
    content/
    calculation/
    persistence/
  ui/
    components/
    screens/
    forms/
  tests/
```

The exact framework and directory names remain implementation decisions until the repository's runtime conventions are inspected and selected.

## 5. Initial domain contracts

- `Rashi`: stable ID, canonical name, localized names, ordering, symbol metadata.
- `WeeklyHoroscope`: rashi ID, period, locale, sections, source reference, status, timestamp.
- `BirthProfile`: date, place, time, timezone, purpose/consent metadata.
- `AstrologyChartRequest`: birth profile plus calculation configuration.
- `AstrologyChartResult`: provider version, method, chart data, warnings, provenance.
- `AssistantAnswer`: question, answer, locale, answer type, source references, limitation notice.
- `LocaleResource`: locale, key, value, version, review status.

## 6. First vertical slice

The first executable slice shall include:

1. Hindi/English language switching.
2. All 12 rashi cards.
3. One detailed weekly horoscope view using clearly labelled demo content.
4. Birth-data form with validation and reset.
5. Assistant response using a mock service and explicit limitation language.
6. Responsive mobile layout suitable for iPhone use.
7. Unit tests for locale resolution and birth-data validation.

## 7. Dependencies and blockers

### Required before production claims

- Approved astrology tradition and terminology.
- Approved ephemeris/calculation provider and licensing.
- Approved ayanamsa and house system.
- Historical timezone and location policy.
- Approved weekly content authority and editorial workflow.
- Privacy and retention decision.

### Non-blocking for the demo slice

- Native Android packaging.
- Authentication.
- Permanent birth-profile storage.
- Paid consultation features.
- Full professional astrology features.

## 8. Traceability

- Requirements artifact: `REQUIREMENTS_v0.1.md`
- Architecture/UX artifact: `ARCHITECTURE_UX_SPEC_v0.1.md`
- Registration artifact: `DEVELOPMENT_STUDIO_REGISTRATION_v0.1.json`
- Implementation plan: `IMPLEMENTATION_PLAN_v0.1.md`
- Future links: source code, test plan, test results, build log, and release artifact.

## 9. Exit criteria

Implementation planning is complete when:

- The first vertical slice is accepted.
- Framework/runtime selection is recorded.
- Domain contracts are mapped to source files.
- Required tasks and dependencies are registered.
- Calculation and content blockers are explicitly tracked.
- Test and build evidence requirements are defined.

## 10. Authority statement

This document is an approved project implementation-planning artifact. It does not modify the canonical KALP architecture, does not authorize unsupported astrology claims, and does not represent completed implementation.
