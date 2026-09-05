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
  if (!SUPABASE_ANON_KEY) {
    throw new Error("Supabase browser key is not configured in this deployment.");
  }

  const response = await fetch(`${SUPABASE_URL}/auth/v1/signup`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      apikey: SUPABASE_ANON_KEY
    },
    body: JSON.stringify({})
  });

  const result = await response.json() as { access_token?: string; error_description?: string; msg?: string };
  if (!response.ok || !result.access_token) {
    throw new Error(result.error_description || result.msg || `Authentication failed with HTTP ${response.status}`);
  }

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

  const grid = byId<HTMLDivElement>("rashiGrid");
  grid.replaceChildren(...rashis.map((rashi) => {
    const button = document.createElement("button");
    button.className = "rashi";
    button.type = "button";
    button.textContent = `${rashi.symbol} ${rashi.names[locale]}`;
    button.setAttribute("aria-pressed", String(rashi.id === selected));
    button.addEventListener("click", () => {
      selected = rashi.id;
      render();
    });
    return button;
  }));

  const weekly = runtime.weekly(selected, locale);
  byId("selectedName").textContent = rashis.find((rashi) => rashi.id === selected)?.names[locale] ?? "";
  byId("weeklyText").textContent = weekly.summary;
}

function displayValue(value: unknown): string {
  if (value === null || value === undefined || value === "") return "—";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

function renderKundliResult(data: unknown, place: string): void {
  const output = byId<HTMLDivElement>("answer");
  output.replaceChildren();

  const heading = document.createElement("h3");
  heading.textContent = locale === "hi-IN" ? "वास्तविक वैदिक कुंडली" : "Live Vedic Kundli";
  output.appendChild(heading);

  const location = document.createElement("p");
  location.textContent = `${locale === "hi-IN" ? "जन्म स्थान" : "Birth place"}: ${place}`;
  output.appendChild(location);

  const pre = document.createElement("pre");
  pre.className = "kundli-json";
  pre.textContent = JSON.stringify(data, null, 2);
  output.appendChild(pre);
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
  output.textContent = locale === "hi-IN" ? "कुंडली डेटा प्राप्त हो रहा है…" : "Fetching Kundli data…";
  button.disabled = true;
  button.textContent = locale === "hi-IN" ? "कुंडली डेटा प्राप्त हो रहा है…" : "Fetching Kundli data…";

  try {
    const token = await getAnonymousAccessToken();
    const response = await fetch(KUNDLI_ENDPOINT, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({
        datetime: `${date}T${time}:00+05:30`,
        coordinates: `${latitude},${longitude}`
      })
    });

    const result = await response.json() as {
      status?: string;
      code?: string;
      message?: string;
      data?: unknown;
    };

    if (!response.ok || result.status !== "SUCCESS") {
      throw new Error(result.message || result.code || `Request failed with HTTP ${response.status}`);
    }

    renderKundliResult(result.data, place);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown request error";
    output.textContent = locale === "hi-IN"
      ? `कुंडली डेटा प्राप्त नहीं हो सका।\n\n${message}`
      : `Kundli data could not be retrieved.\n\n${message}`;
  } finally {
    button.disabled = false;
    button.textContent = locale === "hi-IN" ? "कुंडली डेटा प्राप्त करें" : "Get Kundli data";
  }
});

render();
