import type { Locale, RashiId } from "./domain.js";

export const translations: Record<Locale, Record<string, string>> = {
  "en-IN": {
    appTitle: "Astro Rashi Dashboard",
    weeklyTitle: "Weekly horoscope",
    birthTitle: "Birth details",
    assistantTitle: "Astrologer assistant",
    demoNotice: "Demo content — not a calculated prediction.",
    dateOfBirth: "Date of birth",
    timeOfBirth: "Time of birth",
    placeOfBirth: "Place of birth",
    submit: "Get basic answer",
    incomplete: "Please provide date, time, and place of birth.",
    demoAnswer: "Your birth details are received. A calculation provider is required for a chart-based answer."
  },
  "hi-IN": {
    appTitle: "एस्ट्रो राशि डैशबोर्ड",
    weeklyTitle: "साप्ताहिक राशिफल",
    birthTitle: "जन्म विवरण",
    assistantTitle: "ज्योतिष सहायक",
    demoNotice: "डेमो सामग्री — यह गणना किया हुआ भविष्यफल नहीं है।",
    dateOfBirth: "जन्म तिथि",
    timeOfBirth: "जन्म समय",
    placeOfBirth: "जन्म स्थान",
    submit: "मूल उत्तर प्राप्त करें",
    incomplete: "कृपया जन्म तिथि, समय और स्थान भरें।",
    demoAnswer: "आपका जन्म विवरण प्राप्त हुआ। कुंडली-आधारित उत्तर के लिए गणना प्रदाता आवश्यक है।"
  }
};

export const rashis: Array<{ id: RashiId; symbol: string; names: Record<Locale, string> }> = [
  { id: "mesha", symbol: "♈", names: { "en-IN": "Aries", "hi-IN": "मेष" } },
  { id: "vrishabha", symbol: "♉", names: { "en-IN": "Taurus", "hi-IN": "वृषभ" } },
  { id: "mithuna", symbol: "♊", names: { "en-IN": "Gemini", "hi-IN": "मिथुन" } },
  { id: "karka", symbol: "♋", names: { "en-IN": "Cancer", "hi-IN": "कर्क" } },
  { id: "simha", symbol: "♌", names: { "en-IN": "Leo", "hi-IN": "सिंह" } },
  { id: "kanya", symbol: "♍", names: { "en-IN": "Virgo", "hi-IN": "कन्या" } },
  { id: "tula", symbol: "♎", names: { "en-IN": "Libra", "hi-IN": "तुला" } },
  { id: "vrishchika", symbol: "♏", names: { "en-IN": "Scorpio", "hi-IN": "वृश्चिक" } },
  { id: "dhanu", symbol: "♐", names: { "en-IN": "Sagittarius", "hi-IN": "धनु" } },
  { id: "makara", symbol: "♑", names: { "en-IN": "Capricorn", "hi-IN": "मकर" } },
  { id: "kumbha", symbol: "♒", names: { "en-IN": "Aquarius", "hi-IN": "कुंभ" } },
  { id: "meena", symbol: "♓", names: { "en-IN": "Pisces", "hi-IN": "मीन" } }
];
