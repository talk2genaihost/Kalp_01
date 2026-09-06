import { createAstroRashiRuntime } from "./runtime.js";
import { unavailableCalculationProvider } from "./demo-provider.js";
import { createLiveHoroscopeProvider, fetchLiveHoroscopes, SIGN_MAP } from "./live-horoscope-provider.js";
import { rashis } from "./localization.js";
import type { Locale, Rashi } from "./domain.js";
interface NakshatraAdditionalInfo {
  deity: string | null;
  ganam: string | null;
  symbol: string | null;
  animalSign: string | null;
  nadi: string | null;
  color: string | null;
  bestDirection: string | null;
  syllables: string | null;
  birthStone: string | null;
  gender: string | null;
  planet: string | null;
  enemyYoni: string | null;
}
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
  additionalInfo: NakshatraAdditionalInfo;
}

type ProviderYoga = { name?: unknown; description?: unknown };
type ProviderObject = Record<string, unknown>;

type AnyProviderData = ProviderObject & {
  nakshatra_details?: ProviderObject;
  yoga_details?: unknown;
  mangal_dosha?: ProviderObject;
};

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
  if (typeof value === "string" || typeof value === "number") {
    const v = String(value).trim();
    return v && v.toLowerCase() !== "ok" ? v : null;
  }
  if (typeof value === "object") {
    const record = value as ProviderObject;
    for (const key of ["name", "vedic_name", "label", "value", "sign", "rashi", "title"]) {
      const v = text(record[key]);
      if (v) return v;
    }
  }
  return null;
}
function mapNakshatraAdditionalInfo(
  data: AnyProviderData,
): NakshatraAdditionalInfo {
  const details = data.nakshatra_details;

  const additionalInfo =
    details &&
    typeof details.additional_info === "object" &&
    details.additional_info !== null
      ? (details.additional_info as ProviderObject)
      : {};

  return {
    deity: text(additionalInfo.deity),
    ganam: text(additionalInfo.ganam),
    symbol: text(additionalInfo.symbol),
    animalSign: text(additionalInfo.animal_sign),
    nadi: text(additionalInfo.nadi),
    color: text(additionalInfo.color),
    bestDirection: text(additionalInfo.best_direction),
    syllables: text(additionalInfo.syllables),
    birthStone: text(additionalInfo.birth_stone),
    gender: text(additionalInfo.gender),
    planet: text(additionalInfo.planet),
    enemyYoni: text(additionalInfo.enemy_yoni),
  };
}
function readPath(root: unknown, paths: string[]): string | null {
  for (const path of paths) {
    let current: unknown = root;
    for (const part of path.split(".")) {
      if (!current || typeof current !== "object") {
        current = null;
        break;
      }
      current = (current as ProviderObject)[part];
    }
    const value = text(current);
    if (value) return value;
  }
  return null;
}

function providerData(payload: unknown): AnyProviderData {
  const root = payload as AnyProviderData | null;
  const nested = root?.data;
  if (nested && typeof nested === "object") {
    const nestedData = (nested as ProviderObject).data;
    if (nestedData && typeof nestedData === "object") return nestedData as AnyProviderData;
    return nested as AnyProviderData;
  }
  return root ?? {};
}

function requestedData(payload: unknown): ProviderObject {
  const root = payload as ProviderObject | null;
  return root?.requested && typeof root.requested === "object" ? root.requested as ProviderObject : {};
}

const hindiNames: Record<string, string> = {
  Aries: "मेष",
  Taurus: "वृषभ",
  Gemini: "मिथुन",
  Cancer: "कर्क",
  Leo: "सिंह",
  Virgo: "कन्या",
  Libra: "तुला",
  Scorpio: "वृश्चिक",
  Sagittarius: "धनु",
  Capricorn: "मकर",
  Aquarius: "कुंभ",
  Pisces: "मीन",
  Mesha: "मेष",
  Vrishabha: "वृषभ",
  Mithuna: "मिथुन",
  Karka: "कर्क",
  Simha: "सिंह",
  Kanya: "कन्या",
  Tula: "तुला",
  Vrishchika: "वृश्चिक",
  Dhanu: "धनु",
  Makara: "मकर",
  Kumbha: "कुंभ",
  Meena: "मीन",
  Sun: "सूर्य",
  Moon: "चंद्र",
  Mars: "मंगल",
  Mercury: "बुध",
  Jupiter: "गुरु",
  Venus: "शुक्र",
  Saturn: "शनि",
  Rahu: "राहु",
  Ketu: "केतु",
  Ravi: "सूर्य",
  Budha: "बुध",
  Shani: "शनि",
  "Uttara Phalguni": "उत्तर फाल्गुनी",
  Shatabhisha: "शतभिषा",
};

const yogaNames: Record<string, string> = {
  "Major Yogas": "प्रमुख योग",
  "Chandra Yogas": "चंद्र योग",
  "Soorya Yogas": "सूर्य योग",
  "Inauspicious Yogas": "अशुभ योग",
};

function hindi(value: string | null): string {
  if (!value) return "प्रदाता ने उपलब्ध नहीं कराया";
  return hindiNames[value] ?? yogaNames[value] ?? value;
}

function localizeYoga(value: string): string {
  return value.replace(/Major Yogas|Chandra Yogas|Soorya Yogas|Inauspicious Yogas/g, (name) => yogaNames[name] ?? name)
    .replace(/Your kundli has (\d+) major yogas?/g, "आपकी कुंडली में $1 प्रमुख योग हैं")
    .replace(/Your kundli has (\d+) chandra yogas?\.?/g, "आपकी कुंडली में $1 चंद्र योग हैं।")
    .replace(/Your kundli has (\d+) soorya yogas?\.?/g, "आपकी कुंडली में $1 सूर्य योग हैं।")
    .replace(/Your kundli has (\d+) inauspicious yogas?\.?/g, "आपकी कुंडली में $1 अशुभ योग हैं।")
    .replace(/Your kundli has (\d+) major yogas?\.?/g, "आपकी कुंडली में $1 प्रमुख योग हैं।");
}

function mapKundli(payload: unknown): KundliResult {
  const data = providerData(payload);
  const additionalInfo = mapNakshatraAdditionalInfo(data);
  const requested = requestedData(payload);
  const details = data.nakshatra_details ?? {};
  const nak = (details.nakshatra as ProviderObject | undefined) ?? {};
  const moon = (details.chandra_rasi as ProviderObject | undefined) ?? {};
  const sun = (details.soorya_rasi as ProviderObject | undefined) ?? {};
  const mangalDosha = data.mangal_dosha;

  const requestedBirthPlace = text(requested.birthPlace);
  const yogaDetails: string[] = Array.isArray(data.yoga_details)
    ? data.yoga_details
        .map((item: unknown) => {
          const yoga = (item && typeof item === "object" ? item : {}) as ProviderYoga;
          const name = text(yoga.name);
          const description = text(yoga.description);
          if (name && description) return `${localizeYoga(hindi(name))}: ${localizeYoga(description)}`;
          return name ? localizeYoga(hindi(name)) : description ? localizeYoga(description) : null;
        })
        .filter((item: string | null): item is string => Boolean(item))
    : [];

  const hasMangalik = mangalDosha && typeof mangalDosha === "object"
    ? mangalDosha.has_dosha
    : undefined;

  return {
    birthPlace: requestedBirthPlace ?? hindi(readPath(data, ["birth_place", "birthPlace", "place", "location"])),
    lagna: hindi(readPath(data, [
      "lagna",
      "lagna.name",
      "lagna.sign",
      "ascendant",
      "ascendant.name",
      "ascendant.sign",
      "ascendant_details.ascendant",
      "ascendant_details.ascendant.name",
      "ascendant_details.sign",
      "ascendant_details.sign.name",
      "rising_sign",
      "rising_sign.name",
    ])),
    moonSign: hindi(text(moon.name) ?? text(moon.sign)),
    nakshatra: hindi(text(nak.name) ?? text(nak.sign)),
    nakshatraPada: text(nak.pada) ?? "प्रदाता ने उपलब्ध नहीं कराया",
    nakshatraLord: hindi(text(nak.lord && typeof nak.lord === "object" ? (nak.lord as ProviderObject).name : null) ?? text(nak.lord && typeof nak.lord === "object" ? (nak.lord as ProviderObject).vedic_name : null)),
    tithi: hindi(readPath(data, [
      "tithi",
      "tithi.name",
      "tithi.label",
      "tithi_details.tithi",
      "tithi_details.tithi.name",
      "panchang.tithi",
      "panchang.tithi.name",
      "panchang_details.tithi",
      "panchang_details.tithi.name",
    ])),
    yoga: yogaDetails.length ? yogaDetails.join("\n") : localizeYoga(hindi(readPath(data, ["yoga", "yoga.name", "panchang.yoga", "panchang.yoga.name", "panchang_details.yoga", "panchang_details.yoga.name"]))),
    karana: hindi(readPath(data, ["karana", "karana.name", "karana_details.karana", "karana_details.karana.name", "panchang.karana", "panchang.karana.name", "panchang_details.karana", "panchang_details.karana.name"])),
    sunSign: hindi(text(sun.name) ?? text(sun.sign)),
    manglik: hasMangalik === false ? "मंगल दोष नहीं" : hasMangalik === true ? "मंगल दोष है" : "प्रदाता ने उपलब्ध नहीं कराया",
    dasha: hindi(readPath(data, ["dasha", "dasha.name", "dasha_period", "dasha_period.name", "dasha_periods"])),
 additionalInfo, };
}

function escapeHtml(value: string): string {
  return value.replace(/[&<>"']/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  })[character] ?? character);
}

function renderKundli(payload: unknown): void {
  const result = mapKundli(payload);
  const answer = $("answer");
  answer.className = "notice kundli-result";
  answer.hidden = false;

  const fields: [string, string][] = [
    ["जन्म स्थान", result.birthPlace],
    ["लग्न", result.lagna],
    ["चंद्र राशि", result.moonSign],
    ["नक्षत्र", result.nakshatra],
    ["नक्षत्र पाद", result.nakshatraPada],
    ["नक्षत्र स्वामी", result.nakshatraLord],
    ["तिथि", result.tithi],
    ["योग", result.yoga],
    ["करण", result.karana],
    ["सूर्य राशि", result.sunSign],
    ["मंगल दोष", result.manglik],
    ["दशा", result.dasha],
  ];const additionalInfoFields = [
  ["देवता", result.additionalInfo.deity],
  ["गण", result.additionalInfo.ganam],
  ["प्रतीक", result.additionalInfo.symbol],
  ["पशु चिन्ह", result.additionalInfo.animalSign],
  ["नाड़ी", result.additionalInfo.nadi],
  ["रंग", result.additionalInfo.color],
  ["शुभ दिशा", result.additionalInfo.bestDirection],
  ["अक्षर", result.additionalInfo.syllables],
  ["जन्म रत्न", result.additionalInfo.birthStone],
  ["लिंग", result.additionalInfo.gender],
  ["ग्रह", result.additionalInfo.planet],
  ["शत्रु योनि", result.additionalInfo.enemyYoni],
] as const;

  answer.innerHTML = `<h3>वास्तविक वैदिक कुंडली</h3><p>यह विवरण जन्म-समय और स्थान के आधार पर प्रदाता से प्राप्त हुआ है।</p><div class="kundli-grid">${fields
    .map(([label, value]) => `<div class="kundli-item"><span class="kundli-item-label">${label}</span><strong>${escapeHtml(value).replace(/\n/g, "<br>")}</strong></div>`)
    .join("")}</div><details class="kundli-additional-info">
  <summary>नक्षत्र की विस्तृत जानकारी</summary>
  <div class="kundli-grid kundli-additional-grid">
    ${additionalInfoFields
      .map(
        ([label, value]) => `
          <div class="kundli-field">
            <span class="kundli-label">${label}</span>
            <strong>${escapeHtml(value ?? "प्रदाता ने उपलब्ध नहीं कराया")}</strong>
          </div>
        `,
      )
      .join("")}
  </div>
</details><details><summary>पूरा प्रदाता डेटा देखें</summary><pre class="kundli-json">${escapeHtml(JSON.stringify(payload, null, 2))}</pre></details>`;
}

async function getAccessToken(): Promise<string> {
  if (accessToken) return accessToken;
  if (!SUPABASE_ANON_KEY) throw new Error("Supabase browser key is not configured in this build.");

  const response = await fetch(`${SUPABASE_URL}/auth/v1/signup`, {
    method: "POST",
    headers: { apikey: SUPABASE_ANON_KEY, "Content-Type": "application/json" },
    body: JSON.stringify({}),
  });
  if (!response.ok) throw new Error(`Authentication failed (${response.status}).`);

  const body = await response.json() as { access_token?: string };
  if (!body.access_token) throw new Error("Authentication did not return an access token.");
  accessToken = body.access_token;
  return accessToken;
}

function renderRashis(): void {
  const grid = $("rashiGrid");
  grid.innerHTML = "";
  rashis.forEach((rashi, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "rashi";
    button.setAttribute("aria-pressed", String(rashi.id === selectedRashi.id));
    button.innerHTML = `<span class="rashi-symbol">${rashi.symbol}</span><span class="rashi-name">${rashi.names[locale]}</span><span class="rashi-index">${index + 1} / 12</span>`;
    button.addEventListener("click", () => {
      selectedRashi = rashi;
      renderRashis();
      renderDaily();
    });
    grid.appendChild(button);
  });
}

function renderDaily(): void {
  const content = runtime.weekly(selectedRashi.id, locale);
  const summary = content.summary?.trim() || "इस राशि के लिए दैनिक संदेश अभी उपलब्ध नहीं है। कृपया थोड़ी देर बाद पुनः प्रयास करें।";
  $("selectedName").textContent = selectedRashi.names[locale];
  $("weeklyText").textContent = summary;
  $("selectedRashiLabel").textContent = `${selectedRashi.names[locale]} — चयनित राशि`;
  $("selectedRashiHint").textContent = liveStatus;
}

async function loadLive(): Promise<void> {
  try {
    const result = await fetchLiveHoroscopes(locale);
    for (const rashi of rashis) {
      const value = result.values.get(SIGN_MAP[rashi.id]);
      if (value?.trim()) liveProvider.setSummary(rashi.id, value.trim());
    }
    liveStatus = "Live daily horoscope · Powered by Sigastra";
    renderDaily();
  } catch (error) {
    liveStatus = "Live horoscope unavailable right now. Please retry later.";
    renderDaily();
    console.error(error);
  }
}

function bind(): void {
  document.getElementById("language")?.remove();
  const form = $("birthForm");
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const button = $("askButton") as HTMLButtonElement;
    const answer = $("answer");
    const birthDate = $("birthDate") as HTMLInputElement;
    const birthTime = $("birthTime") as HTMLInputElement;
    const latitudeInput = $("latitude") as HTMLInputElement;
    const longitudeInput = $("longitude") as HTMLInputElement;
    const birthPlaceInput = $("birthPlace") as HTMLInputElement;
    button.disabled = true;
    answer.hidden = false;
    answer.className = "notice";
    answer.textContent = "कुंडली डेटा प्राप्त किया जा रहा है…";

    try {
      const token = await getAccessToken();
      const response = await fetch(KUNDLI_ENDPOINT, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({
          datetime: `${birthDate.value}T${birthTime.value}:00+05:30`,
          coordinates: `${latitudeInput.value},${longitudeInput.value}`,
          birthPlace: birthPlaceInput.value.trim(),
        }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload?.error ?? `Provider request failed (${response.status}).`);
      renderKundli(payload);
    } catch (error) {
      answer.className = "notice";
      answer.textContent = error instanceof Error ? error.message : "कुंडली डेटा प्राप्त नहीं हो सका।";
    } finally {
      button.disabled = false;
    }
  });

  renderRashis();
  renderDaily();
  void loadLive();
}

bind();
