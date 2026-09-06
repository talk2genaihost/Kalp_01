import type { HoroscopeContentProvider, Locale, RashiId, WeeklyHoroscope } from "./domain.js";

const DAILY_ENDPOINT = "https://sigastra.com/api/v1/daily";

export const SIGN_MAP: Record<RashiId, string> = {
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
  const items = (payload as Record<string, unknown>).items;
  return Array.isArray(items)
    ? items.filter((item): item is SigastraItem => Boolean(item && typeof item === "object"))
    : [];
}

export function createLiveHoroscopeProvider(): HoroscopeContentProvider & {
  setSummary(id: RashiId, summary: string): void;
} {
  const summaries = new Map<RashiId, string>();

  return {
    setSummary(id, summary) {
      summaries.set(id, summary);
    },
    getWeekly(id: RashiId, locale: Locale): WeeklyHoroscope {
      return {
        rashiId: id,
        weekLabel: "Today",
        summary: summaries.get(id) ?? "Loading live horoscope…",
        sourceStatus: summaries.has(id) ? "PROVIDER" : "EDITORIAL",
        locale
      };
    }
  };
}

export async function fetchLiveHoroscopes(
  locale: Locale
): Promise<{ values: Map<string, string>; attribution?: string }> {
  const language = locale === "hi-IN" ? "en" : "en";
  const response = await fetch(`${DAILY_ENDPOINT}?lang=${language}`);
  if (!response.ok) throw new Error(`Live horoscope provider failed (${response.status}).`);

  const payload = await response.json() as Record<string, unknown>;
  const values = new Map<string, string>();

  for (const item of normalize(payload)) {
    const sign = typeof item.sign === "string" ? item.sign.toLowerCase() : "";
    if (sign) values.set(sign, extractText(item));
  }

  return { values, attribution: "https://sigastra.com/partners/api" };
}
