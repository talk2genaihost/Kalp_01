import { rashis, translations } from "./localization.js";
import { createAstroRashiRuntime } from "./runtime.js";
import { demoHoroscopeProvider, unavailableCalculationProvider } from "./demo-provider.js";
import type { Locale, RashiId } from "./domain.js";

const runtime = createAstroRashiRuntime(demoHoroscopeProvider, unavailableCalculationProvider);
const localeMap: Record<string, Locale> = { hi: "hi-IN", en: "en-IN" };
const KUNDLI_ENDPOINT = "https://cfwrgalgscieddkcrtde.supabase.co/functions/v1/astro-kundli";
const SUPABASE_URL = "https://cfwrgalgscieddkcrtde.supabase.co";
const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY as string | undefined;
let locale: Locale = "hi-IN";
let selected: RashiId = rashis[0].id;
let accessToken: string | null = null;

const byId = <T extends HTMLElement>(id: string) => document.getElementById(id) as T;

async function getAnonymousAccessToken(): Promise<string> {
  if (accessToken) return accessToken;
  if (!SUPABASE_ANON_KEY) throw new Error("Supabase browser key is not configured in this deployment.");
  const response = await fetch(`${SUPABASE_URL}/auth/v1/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json", apikey: SUPABASE_ANON_KEY },
    body: JSON.stringify({})
  });
  const result = await response.json() as { access_token?: string; error_description?: string; msg?: string };
  if (!response.ok || !result.access_token) throw new Error(result.error_description || result.msg || `Authentication failed with HTTP ${response.status}`);
  accessToken = result.access_token;
  return accessToken;
}

function render(): void {
  const t = translations[locale];
  byId("title").textContent = t.weeklyTitle;
  byId("subtitle").textContent = t.demoNotice;
  byId("weeklyTitle").textContent = t.weeklyTitle;
  byId("assistantTitle").textContent = t.assistantTitle;
  byId("dateLabel").textContent = t.dateOfBirth;
  byId("timeLabel").textContent = t.timeOfBirth;
  byId("placeLabel").textContent = t.placeOfBirth;
  byId("askButton").textContent = locale === "hi-IN" ? "कुंडली डेटा प्राप्त करें" : "Get Kundli data";
  byId("demoNotice").textContent = t.demoNotice;
  byId("chooseTitle").textContent = locale === "hi-IN" ? "अपनी राशि चुनें" : "Choose your Rashi";
  byId("selectedRashiLabel").textContent = locale === "hi-IN" ? "चयनित राशि" : "Selected Rashi";
  byId("selectedRashiHint").textContent = locale === "hi-IN" ? "राशि चुनने पर उसका साप्ताहिक संदेश यहाँ दिखाई देगा।" : "Select a Rashi to view its weekly message.";

  const grid = byId<HTMLDivElement>("rashiGrid");
  grid.replaceChildren(...rashis.map((rashi, index) => {
    const button = document.createElement("button");
    button.className = "rashi";
    button.type = "button";
    button.innerHTML = `<span class="rashi-symbol">${rashi.symbol}</span><span class="rashi-name">${rashi.names[locale]}</span><span class="rashi-index">${index + 1} / 12</span>`;
    button.setAttribute("aria-pressed", String(rashi.id === selected));
    button.addEventListener("click", () => { selected = rashi.id; render(); });
    return button;
  }));

  const selectedRashi = rashis.find((rashi) => rashi.id === selected);
  const weekly = runtime.weekly(selected, locale);
  byId("selectedName").textContent = selectedRashi?.names[locale] ?? "";
  byId("weeklyText").textContent = weekly.summary;
}

function objectRecord(source: unknown): Record<string, unknown> | null {
  return source && typeof source === "object" ? source as Record<string, unknown> : null;
}

function displayValue(source: unknown): string | null {
  if (typeof source === "string" || typeof source === "number") return String(source);
  const record = objectRecord(source);
  if (!record) return null;
  for (const key of ["name", "vedic_name", "label", "display_name", "value", "sign", "rashi", "planet", "graha"]) {
    const value = record[key];
    if (typeof value === "string" || typeof value === "number") return String(value);
  }
  return null;
}

function firstValue(source: unknown, keys: string[]): string | null {
  const record = objectRecord(source);
  if (!record) return displayValue(source);
  for (const key of keys) {
    const value = displayValue(record[key]);
    if (value) return value;
  }
  for (const value of Object.values(record)) {
    const nested = firstValue(value, keys);
    if (nested) return nested;
  }
  return null;
}

function firstArray(source: unknown, keys: string[]): unknown[] | null {
  const record = objectRecord(source);
  if (!record) return null;
  for (const key of keys) if (Array.isArray(record[key])) return record[key] as unknown[];
  for (const value of Object.values(record)) {
    const nested = firstArray(value, keys);
    if (nested) return nested;
  }
  return null;
}

function formatList(source: unknown, keys: string[]): string | null {
  const values = firstArray(source, keys);
  if (!values?.length) return null;
  const labels = values.map((value) => displayValue(value)).filter((value): value is string => Boolean(value));
  return labels.length ? labels.join(", ") : null;
}

function addResultItem(container: HTMLElement, label: string, value: string | null): void {
  if (!value) return;
  const item = document.createElement("div");
  item.className = "kundli-item";
  const itemLabel = document.createElement("span");
  itemLabel.className = "kundli-item-label";
  itemLabel.textContent = label;
  const itemValue = document.createElement("strong");
  itemValue.textContent = value;
  item.append(itemLabel, itemValue);
  container.appendChild(item);
}

function renderKundliResult(data: unknown, place: string): void {
  const output = byId<HTMLDivElement>("answer");
  output.replaceChildren();
  output.className = "notice kundli-result";

  const heading = document.createElement("h3");
  heading.textContent = locale === "hi-IN" ? "वास्तविक वैदिक कुंडली" : "Live Vedic Kundli";
  output.appendChild(heading);

  const note = document.createElement("p");
  note.textContent = locale === "hi-IN" ? "यह विवरण जन्म-समय और स्थान के आधार पर प्रदाता से प्राप्त हुआ है।" : "These details were received from the provider using the birth time and location.";
  output.appendChild(note);

  const grid = document.createElement("div");
  grid.className = "kundli-grid";
  addResultItem(grid, locale === "hi-IN" ? "जन्म स्थान" : "Birth place", place);
  addResultItem(grid, locale === "hi-IN" ? "लग्न" : "Ascendant", firstValue(data, ["ascendant", "lagna", "ascendant_name", "ascendantSign"]));
  addResultItem(grid, locale === "hi-IN" ? "चंद्र राशि" : "Moon sign", firstValue(data, ["moon_sign", "moonSign", "rashi", "chandra_rashi", "moonRashi"]));
  addResultItem(grid, locale === "hi-IN" ? "नक्षत्र" : "Nakshatra", firstValue(data, ["nakshatra", "birth_star", "birthStar", "janma_nakshatra"]));
  addResultItem(grid, locale === "hi-IN" ? "तिथि" : "Tithi", firstValue(data, ["tithi", "lunar_day", "lunarDay"]));
  addResultItem(grid, locale === "hi-IN" ? "योग" : "Yoga", firstValue(data, ["yoga", "panchang_yoga"]));
  addResultItem(grid, locale === "hi-IN" ? "करण" : "Karana", firstValue(data, ["karana", "panchang_karana"]));
  addResultItem(grid, locale === "hi-IN" ? "सूर्य राशि" : "Sun sign", firstValue(data, ["sun_sign", "sunSign", "surya_rashi"]));
  addResultItem(grid, locale === "hi-IN" ? "ग्रह स्थिति" : "Planetary positions", formatList(data, ["planets", "planetary_positions", "grahas", "planetPositions"]));
  output.appendChild(grid);

  const details = document.createElement("details");
  const summary = document.createElement("summary");
  summary.textContent = locale === "hi-IN" ? "पूरा प्रदाता डेटा देखें" : "View complete provider data";
  details.appendChild(summary);
  const pre = document.createElement("pre");
  pre.className = "kundli-json";
  pre.textContent = JSON.stringify(data, null, 2);
  details.appendChild(pre);
  output.appendChild(details);
}

byId<HTMLSelectElement>("language").addEventListener("change", (event) => {
  locale = localeMap[(event.target as HTMLSelectElement).value] ?? "hi-IN";
  render();
});

byId<HTMLFormElement>("birthForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const output = byId<HTMLDivElement>("answer");
  const button = byId<HTMLButtonElement>("askButton");
  const date = byId<HTMLInputElement>("birthDate").value;
  const time = byId<HTMLInputElement>("birthTime").value;
  const place = byId<HTMLInputElement>("birthPlace").value.trim();
  const latitude = Number(byId<HTMLInputElement>("latitude").value);
  const longitude = Number(byId<HTMLInputElement>("longitude").value);
  output.hidden = false;
  output.className = "notice";
  output.textContent = locale === "hi-IN" ? "कुंडली डेटा प्राप्त हो रहा है…" : "Fetching Kundli data…";
  button.disabled = true;
  button.textContent = locale === "hi-IN" ? "कुंडली डेटा प्राप्त हो रहा है…" : "Fetching Kundli data…";
  try {
    const token = await getAnonymousAccessToken();
    const response = await fetch(KUNDLI_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ datetime: `${date}T${time}:00+05:30`, coordinates: `${latitude},${longitude}` })
    });
    const result = await response.json() as { status?: string; code?: string; message?: string; data?: unknown };
    if (!response.ok || result.status !== "SUCCESS") throw new Error(result.message || result.code || `Request failed with HTTP ${response.status}`);
    renderKundliResult(result.data, place);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown request error";
    output.className = "notice";
    output.textContent = locale === "hi-IN" ? `कुंडली डेटा प्राप्त नहीं हो सका।\n\n${message}` : `Kundli data could not be retrieved.\n\n${message}`;
  } finally {
    button.disabled = false;
    button.textContent = locale === "hi-IN" ? "कुंडली डेटा प्राप्त करें" : "Get Kundli data";
  }
});

render();
