import { rashis, translations } from "./localization.js";
import { createAstroRashiRuntime } from "./runtime.js";
import { demoHoroscopeProvider, unavailableCalculationProvider } from "./demo-provider.js";
import type { Locale, RashiId } from "./domain.js";

const runtime = createAstroRashiRuntime(demoHoroscopeProvider, unavailableCalculationProvider);
const localeMap: Record<string, Locale> = { hi: "hi-IN", en: "en-IN" };
const KUNDLI_ENDPOINT = "https://cfwrgalgscieddkcrtde.supabase.co/functions/v1/astro-kundli";
const SUPABASE_URL = "https://cfwrgalgscieddkcrtde.supabase.co";
const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNmd3JnYWxnc2NpZWRka2NydGRlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODg2MDQyNzYsImV4cCI6MjEwNDE4MDI3Nn0.TwAdY3JdepMp5IFmmogcXJI4VyhN9Yx5iLxqQG7wqrw";
let locale: Locale = "hi-IN";
let selected: RashiId = rashis[0].id;
let accessToken: string | null = null;

const byId = <T extends HTMLElement>(id: string) => document.getElementById(id) as T;

async function getAnonymousAccessToken(): Promise<string> {
  if (accessToken) return accessToken;

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

byId<HTMLSelectElement>("language").addEventListener("change", (event) => {
  locale = localeMap[(event.target as HTMLSelectElement).value] ?? "hi-IN";
  render();
});

byId<HTMLFormElement>("birthForm").addEventListener("submit", async (event) => {
  event.preventDefault();

  const output = byId<HTMLParagraphElement>("answer");
  const button = byId<HTMLButtonElement>("askButton");
  const date = byId<HTMLInputElement>("birthDate").value;
  const time = byId<HTMLInputElement>("birthTime").value;
  const place = byId<HTMLInputElement>("birthPlace").value.trim();
  const latitude = Number(byId<HTMLInputElement>("latitude").value);
  const longitude = Number(byId<HTMLInputElement>("longitude").value);

  output.hidden = false;
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

    output.textContent = locale === "hi-IN"
      ? `जन्म स्थान: ${place}\n\nवास्तविक वैदिक कुंडली डेटा प्राप्त हो गया है।\n\n${JSON.stringify(result.data, null, 2)}`
      : `Birth place: ${place}\n\nLive Vedic Kundli data received.\n\n${JSON.stringify(result.data, null, 2)}`;
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
