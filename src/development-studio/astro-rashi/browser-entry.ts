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

function installLayoutFixes(): void {
  if (document.getElementById("astro-rashi-layout-fixes")) return;
  const style = document.createElement("style");
  style.id = "astro-rashi-layout-fixes";
  style.textContent = `
    #rashiGrid { display:grid; grid-template-columns:repeat(auto-fit,minmax(130px,1fr)); gap:12px; }
    #weeklyText { min-height:4.5rem; white-space:pre-wrap; line-height:1.7; }
    #selectedRashiHint { display:none !important; }
    .rashi { min-width:0; }
    @media (max-width:700px) {
      main, .page, .app, .container { max-width:100%; overflow-x:hidden; }
      .cards, .content-grid, .dashboard-grid { grid-template-columns:1fr !important; }
      h1 { font-size:clamp(2rem,8vw,3.5rem) !important; }
    }
  `;
  document.head.appendChild(style);
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
      renderWeekly();
    });
    grid.appendChild(button);
  });
}

function renderWeekly(): void {
  const content = runtime.weekly(selectedRashi.id, locale);
  const summary = content.summary?.trim() || "इस राशि के लिए साप्ताहिक संदेश अभी उपलब्ध नहीं है। कृपया थोड़ी देर बाद पुनः प्रयास करें।";
  $("selectedName").textContent = selectedRashi.names[locale];
  $("weeklyText").textContent = summary;
  $("selectedRashiLabel").textContent = `${selectedRashi.names[locale]} — Selected sign`;
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
    renderWeekly();
  } catch (error) {
    liveStatus = "Live horoscope unavailable right now. Please retry later.";
    renderWeekly();
    console.error(error);
  }
}

function bind(): void {
  installLayoutFixes();
  document.getElementById("language")?.remove();
  renderRashis();
  renderWeekly();
  void loadLive();
}

bind();
