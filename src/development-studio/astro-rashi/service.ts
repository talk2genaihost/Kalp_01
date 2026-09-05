import type {
  AssistantAnswer,
  AstrologyCalculationProvider,
  BirthProfile,
  HoroscopeContentProvider,
  Locale,
  RashiId,
  WeeklyHoroscope
} from "./domain.js";

export function validateBirthProfile(profile: BirthProfile): Array<keyof BirthProfile> {
  const missing: Array<keyof BirthProfile> = [];
  if (!profile.dateOfBirth.trim()) missing.push("dateOfBirth");
  if (!profile.timeOfBirth.trim()) missing.push("timeOfBirth");
  if (!profile.placeOfBirth.trim()) missing.push("placeOfBirth");
  return missing;
}

export function getWeeklyHoroscope(
  provider: HoroscopeContentProvider,
  rashiId: RashiId,
  locale: Locale
): WeeklyHoroscope {
  return provider.getWeekly(rashiId, locale);
}

export function getBasicAstrologerAnswer(
  provider: AstrologyCalculationProvider,
  profile: BirthProfile
): AssistantAnswer {
  const missingFields = validateBirthProfile(profile);
  if (missingFields.length > 0) {
    return {
      status: "UNAVAILABLE",
      message: "Complete date, time, and place of birth are required.",
      missingFields
    };
  }
  return provider.calculate(profile);
}
