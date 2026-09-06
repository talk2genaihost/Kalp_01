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
Uttara Phalguni: "उत्तर फाल्गुनी",
"Uttara Phalguni": "उत्तर फाल्गुनी",
Shatabhisha: "शतभिषा",
};

function hindi(value: string | null): string {
if (!value) return "प्रदाता ने उपलब्ध नहीं कराया";
return hindiNames[value] ?? value;
}

function mapKundli(payload: unknown): KundliResult {
const data = providerData(payload);
const details = data.nakshatra_details ?? {};
const nak = (details.nakshatra as ProviderObject | undefined) ?? {};
const moon = (details.chandra_rasi as ProviderObject | undefined) ?? {};
const sun = (details.soorya_rasi as ProviderObject | undefined) ?? {};
const mangalDosha = data.mangal_dosha;

const yogaDetails: string[] = Array.isArray(data.yoga_details)
? data.yoga_details
.map((item: unknown) => {
const yoga = (item && typeof item === "object" ? item : {}) as ProviderYoga;
const name = text(yoga.name);
const description = text(yoga.description);
if (name && description) return ${name}: ${description};
return name ?? description;
})
.filter((item: string | null): item is string => Boolean(item))
: [];

const hasMangalik = mangalDosha && typeof mangalDosha === "object"
? mangalDosha.has_dosha
: undefined;

return {
birthPlace: hindi(readPath(data, ["birth_place", "birthPlace", "place", "location"])),
lagna: hindi(readPath(data, ["lagna", "ascendant", "ascendant_details.ascendant", "ascendant_details.sign", "rising_sign"])),
moonSign: hindi(text(moon.name)),
nakshatra: hindi(text(nak.name)),
nakshatraPada: text(nak.pada) ?? "प्रदाता ने उपलब्ध नहीं कराया",
nakshatraLord: hindi(text(nak.lord && typeof nak.lord === "object" ? (nak.lord as ProviderObject).name : null) ?? text(nak.lord && typeof nak.lord === "object" ? (nak.lord as ProviderObject).vedic_name : null)),
tithi: hindi(readPath(data, ["tithi", "tithi_details.tithi", "panchang.tithi", "panchang_details.tithi"])),
yoga: yogaDetails.length ? yogaDetails.join("\n") : hindi(readPath(data, ["yoga", "panchang.yoga", "panchang_details.yoga"])),
karana: hindi(readPath(data, ["karana", "karana_details.karana", "panchang.karana", "panchang_details.karana"])),
sunSign: hindi(text(sun.name)),
manglik: hasMangalik === false ? "मंगल दोष नहीं" : hasMangalik === true ? "मंगल दोष है" : "प्रदाता ने उपलब्ध नहीं कराया",
dasha: hindi(readPath(data, ["dasha", "dasha_period", "dasha_periods"])),
};
}

function escapeHtml(value: string): string {
return value.replace(/[&<>"']/g, (character) => ({
"&": "&",
"<": "<",
">": ">",
'"': """,
"'": "'",
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
];

answer.innerHTML = <h3>वास्तविक वैदिक कुंडली</h3><p>यह विवरण जन्म-समय और स्थान के आधार पर प्रदाता से प्राप्त हुआ है।</p><div class="kundli-grid">${fields
    .map(([label, value]) => <div class="kundli-item"><span class="kundli-item-label">${label}</span><strong>${escapeHtml(value).replace(/\n/g, "<br>")}</strong></div>)
    .join("")}</div><details><summary>पूरा प्रदाता डेटा देखें</summary><pre class="kundli-json">${escapeHtml(JSON.stringify(payload, null, 2))}</pre></details>;
}

async function getAccessToken(): Promise<string> {
if (accessToken) return accessToken;
if (!SUPABASE_ANON_KEY) throw new Error("Supabase browser key is not configured in this build.");

const response = await fetch(${SUPABASE_URL}/auth/v1/signup, {
method: "POST",
headers: { apikey: SUPABASE_ANON_KEY, "Content-Type": "application/json" },
body: JSON.stringify({}),
});
if (!response.ok) throw new Error(Authentication failed (${response.status}).);

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
button.innerHTML = <span class="rashi-symbol">${rashi.symbol}</span><span class="rashi-name">${rashi.names[locale]}</span><span class="rashi-index">${index + 1} / 12</span>;
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
$("selectedRashiLabel").textContent = ${selectedRashi.names[locale]} — चयनित राशि;
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
