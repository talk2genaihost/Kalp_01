import { createAstroRashiRuntime } from "./runtime.js";
import { unavailableCalculationProvider } from "./demo-provider.js";
import { createLiveHoroscopeProvider, fetchLiveHoroscopes, SIGN_MAP } from "./live-horoscope-provider.js";
import { rashis } from "./localization.js";
import type { Locale, Rashi } from "./domain.js";

const liveProvider = createLiveHoroscopeProvider();
const runtime = createAstroRashiRuntime(liveProvider, unavailableCalculationProvider);
const locale: Locale = "en-IN";
let selectedRashi: Rashi = rashis[0];
let liveStatus = "Loading live daily horoscope…";
const $ = <T extends HTMLElement>(id: string) => document.getElementById(id) as T;

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
      renderWeekly();
    });
    grid.appendChild(button);
  });
}

function renderWeekly(): void {
  const content = runtime.weekly(selectedRashi.id, locale);
  $("selectedName").textContent = selectedRashi.names[locale];
  $("weeklyText").textContent = content.summary;
  $("selectedRashiLabel").textContent = `${selectedRashi.names[locale]} — Selected sign`;
  $("selectedRashiHint").textContent = liveStatus;
}

async function loadLive(): Promise<void> {
  try {
    const result = await fetchLiveHoroscopes(locale);
    for (const rashi of rashis) {
      const value = result.values.get(SIGN_MAP[rashi.id]);
      if (value) liveProvider.setSummary(rashi.id, value);
    }
    liveStatus = "Live daily horoscope · Powered by Sigastra";
    renderWeekly();
  } catch (error) {
    liveStatus = "Live horoscope unavailable right now. Please retry later.";
    renderWeekly();
    console.error(error);
  }
}

function bind(): void {
  document.getElementById("language")?.remove();
  renderRashis();
  renderWeekly();
  void loadLive();
}

bind();
