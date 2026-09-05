import test from "node:test";
import assert from "node:assert/strict";
import { translations, rashis } from "../src/development-studio/astro-rashi/localization.js";
import type { BirthProfile, HoroscopeContentProvider } from "../src/development-studio/astro-rashi/domain.js";
import { getBasicAstrologerAnswer, getWeeklyHoroscope, validateBirthProfile } from "../src/development-studio/astro-rashi/service.js";

test("catalogue contains twelve rashis in both supported locales", () => {
  assert.equal(rashis.length, 12);
  for (const rashi of rashis) {
    assert.ok(rashi.names["en-IN"]);
    assert.ok(rashi.names["hi-IN"]);
    assert.ok(rashi.symbol);
  }
});

test("localization contains the first-slice keys", () => {
  const keys = ["appTitle", "weeklyTitle", "birthTitle", "assistantTitle", "submit"];
  for (const locale of ["en-IN", "hi-IN"] as const) {
    for (const key of keys) assert.ok(translations[locale][key]);
  }
});

test("birth validation reports all missing fields", () => {
  const profile: BirthProfile = { dateOfBirth: "", timeOfBirth: "", placeOfBirth: "" };
  assert.deepEqual(validateBirthProfile(profile), ["dateOfBirth", "timeOfBirth", "placeOfBirth"]);
});

test("basic assistant does not invoke calculation with incomplete input", () => {
  let invoked = false;
  const provider = { calculate: () => { invoked = true; return { status: "DEMO" as const, message: "unexpected", missingFields: [] }; } };
  const answer = getBasicAstrologerAnswer(provider, { dateOfBirth: "", timeOfBirth: "10:00", placeOfBirth: "Delhi" });
  assert.equal(answer.status, "UNAVAILABLE");
  assert.deepEqual(answer.missingFields, ["dateOfBirth"]);
  assert.equal(invoked, false);
});

test("weekly service delegates to the content provider", () => {
  const expected = { rashiId: "mesha" as const, weekLabel: "Demo week", summary: "Demo summary", sourceStatus: "DEMO" as const, locale: "hi-IN" as const };
  const provider: HoroscopeContentProvider = { getWeekly: () => expected };
  assert.deepEqual(getWeeklyHoroscope(provider, "mesha", "hi-IN"), expected);
});
