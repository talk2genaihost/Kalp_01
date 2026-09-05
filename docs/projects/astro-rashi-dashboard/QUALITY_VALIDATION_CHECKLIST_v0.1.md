# Astro Rashi Dashboard — Quality Validation Checklist v0.1

- Project: `KALP-PROJ-ASTRO-RASHI-001`
- Parent system: KALP Development Studio
- Scope: first executable web vertical slice
- Status: `READY_FOR_VALIDATION`
- Evidence baseline: successful GitHub Actions run `33942464639`

## 1. Build and test gate

- [x] Dependency installation completes in the repository workflow.
- [x] TypeScript build completes.
- [x] Astro Rashi browser build completes.
- [x] Test suite completes.
- [ ] Validation evidence is reviewed against the approved requirements and architecture.

## 2. Functional acceptance

- [ ] Hindi and English language switching updates all visible labels and content.
- [ ] All 12 rashi cards are rendered with stable identifiers.
- [ ] Selected rashi state is visually and semantically exposed.
- [ ] Weekly horoscope content is explicitly labelled as demo/general guidance.
- [ ] Birth-data form accepts date, time, and place inputs.
- [ ] Required-field and invalid-input validation is deterministic.
- [ ] Reset behavior clears the birth-data workflow.
- [ ] Assistant response uses the mock service and exposes limitation language.
- [ ] Unavailable calculation behavior is distinguishable from calculated output.

## 3. Accessibility acceptance

- [ ] Keyboard navigation reaches language control, rashi cards, form fields, and submit/reset controls.
- [ ] Selected rashi state is exposed through an accessible state attribute.
- [ ] Form labels are associated with their controls.
- [ ] Validation and assistant results are announced or otherwise discoverable.
- [ ] Focus indicators remain visible.
- [ ] Layout remains usable at narrow mobile widths.

## 4. Privacy and data-boundary acceptance

- [ ] Birth data is not written to ordinary logs.
- [ ] Privacy notice is visible before submission or persistence.
- [ ] Reset/delete behavior removes entered birth data from the active UI state.
- [ ] No permanent birth-profile storage is claimed.
- [ ] No production astrology calculation is claimed.

## 5. Provenance and content acceptance

- [ ] Demo horoscope content includes source/reference metadata where displayed.
- [ ] Locale and period metadata remain consistent with the selected rashi.
- [ ] Assistant answers distinguish general guidance, calculated output, interpretation, and unavailable states.
- [ ] Unresolved tradition, ephemeris, ayanamsa, house-system, timezone, and content-authority decisions remain explicitly tracked.

## 6. Release decision

- `READY_FOR_VALIDATION`: build and automated test gate passed; manual/product validation pending.
- `ACCEPTED_FOR_DEMO`: all required first-slice checks pass and limitations remain visible.
- `BLOCKED`: any critical functional, accessibility, privacy, or provenance check fails.
- `NOT_READY_FOR_PRODUCTION`: production calculation, content authority, privacy retention, and licensing decisions remain unresolved.

## 7. Next execution action

Perform the checklist against the browser slice, record pass/fail evidence, and create a remediation task for each failed check. Do not mark the project production-ready until the blockers in the approved implementation plan are resolved.

## Authority statement

This is a project-level validation artifact. It does not modify canonical KALP architecture or authorize unsupported astrology claims.
