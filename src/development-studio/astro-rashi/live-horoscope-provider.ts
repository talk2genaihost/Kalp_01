import type { HoroscopeContentProvider, Locale, RashiId, WeeklyHoroscope } from "./domain.js";

const DAILY_ENDPOINT = "https://sigastra.com/api/v1/daily";
const SIGN_MAP: Record<RashiId, string> = {
  mesha: "aries",
  vrishabha: "taurus",
  mithuna: "gemini",
  karka: "cancer",
  simha: "leo",
  kanya: "virgo",
  tula: "libra",
  vrishchika: "scorpio",
  dhanu: "sagittarius",
  makara: "capricorn",
  kumbha: "aquarius",
  meena: "pisces"
};

type SigastraItem = Record<string, unknown>;

function extractText(item: SigastraItem): string {
  for (const key of ["teaser", "text", "summary", "description", "prediction"]) {
    const value = item[key];
    if (typeof value === "string" && value.trim()) return value.trim();
  }
  return "Live horoscope text is unavailable for this sign.";
}

function normalize(payload: unknown): SigastraItem[] {
  if (!payload || typeof payload !== "object") return [];
  const root = payload as Record<string, unknown>;
  const items = root.items;
  if (Array.isArray(items)) return items.filter((item): item is SigastraItem => Boolean(item && typeof item === "object"));
  return [];
}

export function createLiveHoroscopeProvider(): HoroscopeContentProvider {
  const cache = new Map<string, Map<string, string>>();

  return {
    weekly(rashiId: RashiId, locale: Locale): WeeklyHoroscope {
      const key = `${locale}:daily`;
      const sign = SIGN_MAP[rashiId];
      const cached = cache.get(key)?.get(sign);
      return {
        title: "Live horoscope",
        summary: cached ?? "Loading live horoscope…",
        focus: "General daily guidance",
        advice: "Use this as general guidance, not a guaranteed prediction."
      };
    },
    basicAnswer: () => ({
      title: "Live horoscope provider",
      summary: "Select a Rashi to view live horoscope content.",
      details: []
    })
  };
}

export async function fetchLiveHoroscopes(locale: Locale): Promise<{ values: Map<string, string>; attribution?: string }> {
  const language = locale === "hi-IN" ? "en" : "en";
  const response = await fetch(`${DAILY_ENDPOINT}?lang=${language}`);
  if (!response.ok) throw new Error(`Live horoscope provider failed (${response.status}).`);
  const payload = await response.json() as Record<string, unknown>;
  const values = new Map<string, string>();
  for (const item of normalize(payload)) {
    const sign = typeof item.sign === "string" ? item.sign.toLowerCase() : "";
    if (sign) values.set(sign, extractText(item));
  }
  const attribution = typeof payload.attribution === "object" && payload.attribution
    ? String((payload.attribution as Record<string, unknown>).localizedHref ?? "")
    : undefined;
  return { values, attribution };
}

export { SIGN_MAP };
