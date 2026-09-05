import type {
  AssistantAnswer,
  AstrologyCalculationProvider,
  BirthProfile,
  HoroscopeContentProvider,
  Locale,
  RashiId,
  WeeklyHoroscope
} from "./domain.js";
import { getBasicAstrologerAnswer, getWeeklyHoroscope } from "./service.js";

export interface AstroRashiRuntime {
  weekly(rashiId: RashiId, locale: Locale): WeeklyHoroscope;
  basicAnswer(profile: BirthProfile): AssistantAnswer;
}

export function createAstroRashiRuntime(
  contentProvider: HoroscopeContentProvider,
  calculationProvider: AstrologyCalculationProvider
): AstroRashiRuntime {
  return {
    weekly: (rashiId, locale) => getWeeklyHoroscope(contentProvider, rashiId, locale),
    basicAnswer: (profile) => getBasicAstrologerAnswer(calculationProvider, profile)
  };
}
