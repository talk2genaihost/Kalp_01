# Framework and Runtime Selection v0.1

- Project ID: `KALP-PROJ-ASTRO-RASHI-001`
- Parent: KALP Development Studio
- Status: PROPOSED / READY FOR IMPLEMENTATION
- Decision type: project-level implementation decision

## Selection

The first executable slice will use a dependency-light, web-first implementation:

- TypeScript for domain and application logic.
- Semantic HTML for the initial UI surface.
- CSS for responsive presentation and theme tokens.
- Browser-native ES modules for execution.
- No astrology calculation dependency in the first slice.
- Demo content and a mock assistant adapter behind explicit interfaces.

React/Vite remain viable follow-on choices, but are not introduced until the repository's runtime dependencies and build pipeline are explicitly established. This avoids adding an unverified framework dependency to the first vertical slice.

## Rationale

1. The repository already uses TypeScript and has a source-governed Development Studio foundation.
2. A dependency-light slice can be opened directly in a browser and later embedded in a React or Android WebView shell.
3. Domain contracts remain independent of the presentation technology.
4. The first slice must demonstrate the UX and localization behavior without implying that horoscope calculation is production-ready.

## Runtime boundaries

The first slice contains:

- Twelve rashi cards.
- Hindi/English language switching.
- A weekly horoscope detail panel using clearly labeled demo content.
- Birth-detail form validation.
- A mock assistant response based on submitted birth details.

It does not contain:

- Ephemeris calculations.
- Natal-chart computation.
- Persisted birth data.
- Authentication.
- Paid consultation workflows.
- Production horoscope feeds.

## Acceptance criteria

- Runs without a server-side dependency after repository checkout.
- Works at mobile and desktop widths.
- Language switching changes visible interface text and demo content.
- Birth details are validated before the mock assistant responds.
- Demo and unresolved calculation boundaries are visible to the user.
