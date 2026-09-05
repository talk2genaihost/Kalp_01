import type { AstrologyCalculationProvider, AssistantAnswer, BirthProfile, HoroscopeContentProvider, Locale, RashiId, WeeklyHoroscope } from "./domain.js";
import { rashis } from "./localization.js";

export const demoHoroscopeProvider: HoroscopeContentProvider = {
  getWeekly(rashiId: RashiId, locale: Locale): WeeklyHoroscope {
    const rashi = rashis.find((item) => item.id === rashiId);
    const name = rashi?.names[locale] ?? rashiId;
    return {
      rashiId,
      weekLabel: locale === "hi-IN" ? "डेमो सप्ताह" : "Demo week",
      summary: locale === "hi-IN"
        ? `${name} के लिए यह डेमो साप्ताहिक संकेत है। वास्तविक गणना या संपादकीय भविष्यफल नहीं।`
        : `This is a demo weekly signal for ${name}; it is not a calculated or editorial prediction.`,
      sourceStatus: "DEMO",
      locale
    };
  }
};

export const unavailableCalculationProvider: AstrologyCalculationProvider = {
  calculate(_profile: BirthProfile): AssistantAnswer {
    return {
      status: "UNAVAILABLE",
      message: "A calculation provider is not configured for this first slice.",
      missingFields: []
    };
  }
};
