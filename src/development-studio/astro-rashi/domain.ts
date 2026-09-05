export type Locale = "hi-IN" | "en-IN";

export type RashiId =
  | "mesha" | "vrishabha" | "mithuna" | "karka" | "simha" | "kanya"
  | "tula" | "vrishchika" | "dhanu" | "makara" | "kumbha" | "meena";

export interface Rashi {
  id: RashiId;
  symbol: string;
  names: Record<Locale, string>;
}

export interface WeeklyHoroscope {
  rashiId: RashiId;
  weekLabel: string;
  summary: string;
  sourceStatus: "DEMO" | "EDITORIAL" | "PROVIDER";
  locale: Locale;
}

export interface BirthProfile {
  dateOfBirth: string;
  timeOfBirth: string;
  placeOfBirth: string;
}

export interface AssistantAnswer {
  status: "DEMO" | "CALCULATED" | "UNAVAILABLE";
  message: string;
  missingFields: Array<keyof BirthProfile>;
}

export interface HoroscopeContentProvider {
  getWeekly(rashiId: RashiId, locale: Locale): WeeklyHoroscope;
}

export interface AstrologyCalculationProvider {
  calculate(profile: BirthProfile): AssistantAnswer;
}
