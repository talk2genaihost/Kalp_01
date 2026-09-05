# Astro Rashi Dashboard — Architecture and UX Specification v0.1

## 1. Status and authority

- Project ID: `KALP-PROJ-ASTRO-RASHI-001`
- Artifact ID: `ASTRO-RASHI-ARCH-UX-001`
- Version: `0.1`
- Status: PROPOSED
- Authority: SUPPORTING project artifact; not a canonical KALP architecture contract
- Parent: KALP Development Studio

## 2. Architectural principles

1. Keep presentation, domain logic, content, calculations, and persistence separate.
2. Keep locale-independent data separate from translated labels and content.
3. Preserve provenance for every generated or published result.
4. Treat birth data as private user data and exclude it from ordinary logs.
5. Make calculation providers replaceable through an explicit interface.
6. Do not expose unsupported certainty or guaranteed predictions.
7. Keep the web client and future Android client dependent on shared domain contracts rather than UI-specific logic.

## 3. Logical architecture

```text
Web UI / Future Android UI
        |
Presentation and localization layer
        |
Application services
  - Rashi dashboard service
  - Assistant conversation service
  - Birth-data validation service
        |
Domain interfaces
  - Horoscope content provider
  - Astrology calculation provider
  - Provenance recorder
        |
Adapters
  - Approved content source adapter
  - Approved calculation/ephemeris adapter
  - Persistence adapter
        |
Development Studio traceability
  - Requirements
  - Architecture and UX artifacts
  - Tests
  - Build and release artifacts
```

## 4. Proposed domain objects

- `Rashi`: stable identifier, canonical name, localized names, ordering, symbol metadata.
- `WeeklyHoroscope`: rashi ID, period, locale, content sections, source reference, status, created timestamp.
- `BirthProfile`: date, place, time, timezone, consent/purpose metadata; sensitive fields excluded from display logs.
- `AstrologyChartRequest`: birth profile plus calculation configuration.
- `AstrologyChartResult`: calculation method, provider version, chart data, warnings, provenance.
- `AssistantAnswer`: question, answer, language, answer type, source references, confidence/limitation notice.
- `LocaleResource`: locale, key, translated value, version, review status.

## 5. UX structure

### 5.1 Main navigation

- Home / Weekly Dashboard
- My Rashi
- Astrologer Assistant
- Language
- Privacy and Settings

### 5.2 Weekly dashboard

1. Header with selected language and week period.
2. Twelve-rashi grid or responsive list.
3. Each card shows rashi name, localized name, short weekly summary, and status.
4. Selecting a card opens the detailed weekly view.
5. Detail view sections remain consistent across languages.
6. Source and period metadata are available without overwhelming the primary reading experience.

### 5.3 Assistant flow

1. Welcome and limitation statement.
2. Language selection or inherited application locale.
3. Birth-data form: date, place, time, timezone confirmation.
4. Validation and missing-data guidance.
5. Question input with suggested basic questions.
6. Answer view with labels distinguishing calculated data, interpretation, general guidance, and unavailable information.
7. Clear option to remove/reset entered birth details.

### 5.4 Responsive behavior

- Mobile-first layout.
- One-column rashi cards on narrow screens; adaptive grid on wider screens.
- Assistant form divided into short, accessible sections.
- No essential information conveyed only by color.
- Touch targets and text sizing suitable for phone use.

## 6. Localization design

- Use locale keys rather than hardcoded interface strings.
- Initial locales: `hi-IN`, `en-IN`.
- Store rashi identifiers independently from translated names.
- Support pluralization, date formatting, time formatting, and directionality through the localization layer.
- Define fallback behavior for missing translations.
- Do not translate calculation identifiers, source IDs, or machine-readable status values.
- Review Hindi terminology before production publication.

## 7. Data and privacy design

- Birth details are collected only for the assistant workflow.
- Default behavior should avoid permanent storage unless the user explicitly enables it.
- Redact date, time, and place of birth from application logs and analytics.
- Provide reset/delete controls in the UX.
- Separate public weekly content from private birth profiles.

## 8. Calculation and content safeguards

The following are unresolved and block production-grade astrology claims:

- Astrology tradition and calculation convention.
- Ephemeris data source and licensing.
- Ayanamsa and house-system selection.
- Timezone and historical location handling.
- Content editorial authority and review process.
- Explanation of uncertainty and limitations.

Until approved, the system may use clearly labelled demo or general guidance content only.

## 9. Testing strategy

- Unit tests for locale resolution and fallback behavior.
- Unit tests for birth-data validation.
- Contract tests for calculation-provider adapters.
- Snapshot or component tests for all 12 rashi cards in Hindi and English.
- Accessibility tests for forms, navigation, and error states.
- Privacy tests confirming sensitive birth data is not written to ordinary logs.
- Integration tests for provenance and source-reference propagation.

## 10. Release gates

Before implementation is marked release-ready:

1. Requirements approved.
2. Architecture and UX specification approved.
3. Calculation and content authorities registered.
4. Hindi and English content reviewed.
5. Privacy behavior tested.
6. Build and test artifacts recorded in Development Studio.
7. Android packaging decision documented.
