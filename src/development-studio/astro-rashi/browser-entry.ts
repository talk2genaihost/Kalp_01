import { rashis, translations } from "./localization.js";
import { createAstroRashiRuntime } from "./runtime.js";
import { demoHoroscopeProvider, unavailableCalculationProvider } from "./demo-provider.js";
import type { Locale, RashiId } from "./domain.js";

const runtime = createAstroRashiRuntime(demoHoroscopeProvider, unavailableCalculationProvider);
const localeMap: Record<string, Locale> = { hi: "hi-IN", en: "en-IN" };
const KUNDLI_ENDPOINT = "https://cfwrgalgscieddkcrtde.supabase.co/functions/v1/astro-kundli";
let locale: Locale = "hi-IN";
let selected: RashiId = rashis[0].id;

const byId = <T extends HTMLElement>(id: string) => document.getElementById(id) as T;

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
    const response = await fetch(KUNDLI_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
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
