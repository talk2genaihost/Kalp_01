import { rashis, translations } from "./localization.js";
import { createAstroRashiRuntime } from "./runtime.js";
import { demoHoroscopeProvider, unavailableCalculationProvider } from "./demo-provider.js";
import type { Locale, RashiId } from "./domain.js";

const runtime = createAstroRashiRuntime(demoHoroscopeProvider, unavailableCalculationProvider);
const localeMap: Record<string, Locale> = { hi: "hi-IN", en: "en-IN" };
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
  byId("askButton").textContent = t.submit;
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

byId<HTMLFormElement>("birthForm").addEventListener("submit", (event) => {
  event.preventDefault();
  const answer = runtime.basicAnswer({
    dateOfBirth: byId<HTMLInputElement>("birthDate").value,
    timeOfBirth: byId<HTMLInputElement>("birthTime").value,
    placeOfBirth: byId<HTMLInputElement>("birthPlace").value
  });
  const output = byId<HTMLParagraphElement>("answer");
  output.hidden = false;
  output.textContent = answer.message;
});

render();
