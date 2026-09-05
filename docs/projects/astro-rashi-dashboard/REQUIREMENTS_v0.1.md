# Astro Rashi Dashboard — Requirements Specification v0.1

## 1. Registration

- Project ID: `KALP-PROJ-ASTRO-RASHI-001`
- Project name: Astro Rashi Dashboard
- Parent system: KALP Development Studio
- Status: APPROVED
- Requirement status: APPROVED BY PROJECT OWNER
- Approval decision: Explicit user approval recorded on 2026-09-05
- Platform: Web-first, Android-ready
- Deployment mode: HYBRID (proposed)
- Initial locales: `hi-IN`, `en-IN`

## 2. Objective

Create a multilingual dashboard that presents weekly horoscope content for all 12 राशियाँ and provides a basic astrologer assistant using date of birth, place of birth, and time of birth.

## 3. Functional requirements

### FR-01 — Twelve-rashi dashboard
The system shall display all 12 राशियाँ and allow the user to select one rashi for detailed weekly content.

### FR-02 — Weekly content
Each rashi shall support a weekly overview with clearly labelled content sections. Content must identify its source, period, language, and publication status.

### FR-03 — Multilingual interface
The system shall support Hindi and English from the first release. Locale-dependent labels, navigation, validation messages, and help text shall be externalized from application logic.

### FR-04 — Localized content
Rashi content shall support a locale key and translated variants. Missing translations shall be visibly marked or fall back according to an explicit, configurable policy.

### FR-05 — Birth details
The assistant shall accept date of birth, place of birth, and time of birth as separate fields, with validation and timezone/location handling recorded.

### FR-06 — Basic assistant
The assistant shall answer basic astrology-related questions using available birth data and clearly state when an answer is general guidance, calculated output, or unavailable.

### FR-07 — Calculation boundary
Astrological calculations shall be implemented as a separate service boundary. The calculation method, ephemeris/source, ayanamsa, house system, timezone rules, and accuracy limitations must be specified before production use.

### FR-08 — Provenance
User-facing horoscope and assistant outputs shall retain references to the content source, calculation method, locale, and generation timestamp where applicable.

### FR-09 — Privacy
Birth details shall be treated as user-provided personal data. The design shall minimize collection, provide clear purpose, and avoid exposing details in logs or analytics by default.

### FR-10 — Android readiness
The business domain, localization resources, validation rules, and calculation interfaces shall remain portable for a future Android client.

## 4. Non-functional requirements

- Responsive layout for mobile and desktop.
- Accessible controls, readable typography, and keyboard navigation.
- Deterministic validation and error states.
- Testable calculation and localization services.
- No production prediction claims without approved calculation and content sources.
- Traceability from requirement to architecture, implementation, and test artifact.

## 5. Out of scope for v0.1

- Paid consultations or payment processing.
- Automated medical, legal, financial, or life-critical advice.
- Guaranteed predictions.
- Full professional astrology suite until calculation specifications are approved.
- Native Android packaging before the web architecture is validated.

## 6. Open decisions

1. Approved astrology calculation standard and provider.
2. Supported astrology tradition and terminology.
3. Weekly content authority and editorial workflow.
4. Additional languages beyond Hindi and English.
5. Authentication and persistence policy for birth details.
6. Offline behavior and caching policy.

## 7. Acceptance criteria for requirements approval

- All FR and NFR items have an owner and trace reference.
- Calculation and content authority gaps are explicitly resolved or marked blocked.
- Hindi and English localization strategy is reviewed.
- Privacy and data-retention decisions are approved.
