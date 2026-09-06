import { createAstroRashiRuntime } from "./runtime.js";
import { unavailableCalculationProvider } from "./demo-provider.js";
import { createLiveHoroscopeProvider, fetchLiveHoroscopes, SIGN_MAP } from "./live-horoscope-provider.js";
import { rashis } from "./localization.js";
import type { Locale, Rashi } from "./domain.js";

interface KundliResult {
  birthPlace: string;
  lagna: string;
  moonSign: string;
  nakshatra: string;
  nakshatraPada: string;
  nakshatraLord: string;
  tithi: string;
  yoga: string;
  karana: string;
  sunSign: string;
  manglik: string;
  dasha: string;
}

type ProviderYoga = { name?: unknown; description?: unknown };
type ProviderObject = Record<string, unknown>;
type AnyProviderData = ProviderObject & { nakshatra_details?: ProviderObject; yoga_details?: unknown; mangal_dosha?: ProviderObject };

const liveProvider = createLiveHoroscopeProvider();
const runtime = createAstroRashiRuntime(liveProvider, unavailableCalculationProvider);
const KUNDLI_ENDPOINT = "https://cfwrgalgscieddkcrtde.supabase.co/functions/v1/astro-kundli";
const SUPABASE_URL = "https://cfwrgalgscieddkcrtde.supabase.co";
const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY as string | undefined;
const locale: Locale = "hi-IN";
let selectedRashi: Rashi = rashis[0];
let accessToken: string | null = null;
let liveStatus = "Loading live daily horoscope…";
const $ = <T extends HTMLElement>(id: string) => document.getElementById(id) as T;

function text(value: unknown): string | null {
  if (value === null || value === undefined) return null;
  if (typeof value === "string" || typeof value === "number") { const v = String(value).trim(); return v && v.toLowerCase() !== "ok" ? v : null; }
  if (typeof value === "object") { const record = value as ProviderObject; for (const key of ["name", "vedic_name", "label", "value", "sign", "rashi", "title"]) { const v = text(record[key]); if (v) return v; } }
  return null;
}
function readPath(root: unknown, paths: string[]): string | null { for (const path of paths) { let current: unknown = root; for (const part of path.split(".")) { if (!current || typeof current !== "object") { current = null; break; } current = (current as ProviderObject)[part]; } const value = text(current); if (value) return value; } return null; }
function providerData(payload: unknown): AnyProviderData { const root = payload as AnyProviderData | null; const nested = root?.data; if (nested && typeof nested === "object") { const nestedData = (nested as ProviderObject).data; if (nestedData && typeof nestedData === "object") return nestedData as AnyProviderData; return nested as AnyProviderData; } return root ?? {}; }
function requestedData(payload: unknown): ProviderObject { const root = payload as ProviderObject | null; return root?.requested && typeof root.requested === "object" ? root.requested as ProviderObject : {}; }

const hindiNames: Record<string, string> = { Aries: "मेष", Taurus: "वृषभ", Gemini: "मिथुन", Cancer: "कर्क", Leo: "सिंह", Virgo: "कन्या", Libra: "तुला", Scorpio: "वृश्चिक", Sagittarius: "धनु", Capricorn: "मकर", Aquarius: "कुंभ", Pisces: "मीन", Mesha: "मेष", Vrishabha: "वृषभ", Mithuna: "मिथुन", Karka: "कर्क", Simha: "सिंह", Kanya: "कन्या", Tula: "तुला", Vrishchika: "वृश्चिक", Vrischika: "वृश्चिक", Dhanu: "धनु", Makara: "मकर", Kumbha: "कुंभ", Meena: "मीन", Sun: "सूर्य", Moon: "चंद्र", Mars: "मंगल", Mercury: "बुध", Jupiter: "गुरु", Venus: "शुक्र", Saturn: "शनि", Rahu: "राहु", Ketu: "केतु", Ravi: "सूर्य", Budha: "बुध", Shani: "शनि", "Uttara Phalguni": "उत्तर फाल्गुनी", Shatabhisha: "शतभिषा" };
function hindi(value: string | null): string { return value ? hindiNames[value] ?? value : "प्रदाता ने उपलब्ध नहीं कराया"; }

function mapKundli(payload: unknown): KundliResult {
  const data = providerData(payload); const requested = requestedData(payload); const details = data.nakshatra_details ?? {};
  const nak = (details.nakshatra as ProviderObject | undefined) ?? {}; const moon = (details.chandra_rasi as ProviderObject | undefined) ?? {}; const sun = (details.soorya_rasi as ProviderObject | undefined) ?? {};
  const mangalDosha = data.mangal_dosha; const yogaDetails: string[] = Array.isArray(data.yoga_details) ? data.yoga_details.map((item: unknown) => { const yoga = (item && typeof item === "object" ? item : {}) as ProviderYoga; const name = text(yoga.name); const description = text(yoga.description); return name && description ? `${name}: ${description}` : name ?? description; }).filter((item: string | null): item is string => Boolean(item)) : [];
  const hasMangalik = mangalDosha && typeof mangalDosha === "object" ? mangalDosha.has_dosha : undefined;
  return {
    birthPlace: text(requested.birthPlace) ?? hindi(readPath(data, ["birth_place", "birthPlace", "place", "location"])),
    lagna: hindi(readPath(data, ["lagna", "lagna.name", "lagna.sign", "ascendant", "ascendant.name", "ascendant.sign", "ascendant_details.ascendant", "ascendant_details.ascendant.name", "ascendant_details.sign", "ascendant_details.sign.name", "rising_sign", "rising_sign.name"])),
    moonSign: hindi(text(moon.name) ?? text(moon.sign)), nakshatra: hindi(text(nak.name) ?? text(nak.sign)), nakshatraPada: text(nak.pada) ?? "प्रदाता ने उपलब्ध नहीं कराया",
    nakshatraLord: hindi(text(nak.lord && typeof nak.lord === "object" ? (nak.lord as ProviderObject).name : null) ?? text(nak.lord && typeof nak.lord === "object" ? (nak.lord as ProviderObject).vedic_name : null)),
    tithi: hindi(readPath(data, ["tithi", "tithi.name", "tithi.label", "tithi_details.tithi", "tithi_details.tithi.name", "panchang.tithi", "panchang.tithi.name", "panchang_details.tithi", "panchang_details.tithi.name"])),
    yoga: yogaDetails.length ? yogaDetails.join("\n") : hindi(readPath(data, ["yoga", "yoga.name", "panchang.yoga", "panchang.yoga.name", "panchang_details.yoga", "panchang_details.yoga.name"])),
    karana: hindi(readPath(data, ["karana", "karana.name", "karana_details.karana", "karana_details.karana.name", "panchang.karana", "panchang.karana.name", "panchang_details.karana", "panchang_details.karana.name"])),
    sunSign: hindi(text(sun.name) ?? text(sun.sign)), manglik: hasMangalik === false ? "मंगल दोष नहीं" : hasMangalik === true ? "मंगल दोष है" : "प्रदाता ने उपलब्ध नहीं कराया",
    dasha: hindi(readPath(data, ["dasha", "dasha.name", "dasha_period", "dasha_period.name", "dasha_periods"])),
  };
}
