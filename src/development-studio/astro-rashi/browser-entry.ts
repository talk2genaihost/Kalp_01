import { createAstroRashiRuntime } from "./runtime.js";
import { demoHoroscopeProvider, unavailableCalculationProvider } from "./demo-provider.js";
import { translations, rashiList, type Locale } from "./localization.js";
import type { KundliResult } from "./domain.js";

const runtime = createAstroRashiRuntime(demoHoroscopeProvider, unavailableCalculationProvider);
const localeMap: Record<string, Locale> = { hi: "hi-IN", en: "en-IN" };

const KUNDLI_ENDPOINT =
  "https://cfwrgalgscieddkcrtde.supabase.co/functions/v1/astro-kundli";
const SUPABASE_URL = "https://cfwrgalgscieddkcrtde.supabase.co";
const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY as string | undefined;

let locale: Locale = "hi-IN";
let selectedRashi = rashiList[0];
let accessToken: string | null = null;

const $ = <T extends HTMLElement>(id: string) =>
  document.getElementById(id) as T;

function text(value: unknown): string | null {
  if (value === null || value === undefined) return null;

  if (typeof value === "string" || typeof value === "number") {
    const normalized = String(value).trim();

    if (!normalized || normalized.toLowerCase() === "ok") {
      return null;
    }

    return normalized;
  }

  if (typeof value === "object") {
    const record = value as Record<string, unknown>;

    for (const key of [
      "name",
      "vedic_name",
      "label",
      "value",
      "sign",
      "rashi",
      "title",
    ]) {
      const nested = text(record[key]);

      if (nested) {
        return nested;
      }
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

      current = (current as Record<string, unknown>)[part];
    }

    const value = text(current);

    if (value) {
      return value;
    }
  }

  return null;
}

function providerData(payload: unknown): unknown {
  if (!payload || typeof payload !== "object") {
    return payload;
  }

  const record = payload as Record<string, unknown>;

  return record.data && typeof record.data === "object"
    ? record.data
    : payload;
}

function mapKundli(payload: unknown): KundliResult {
  const data = providerData(payload);

  return {
    birthPlace:
      readPath(data, [
        "birth_place",
        "birthPlace",
        "place",
        "location",
      ]) ?? "—",

    lagna:
      readPath(data, [
        "lagna",
        "ascendant",
        "ascendant_details.ascendant",
        "ascendant_details.sign",
        "rising_sign",
      ]) ?? "—",

    moonSign:
      readPath(data, [
        "moon_sign",
        "moonSign",
        "chandra_rashi",
        "chandra_rashi_details.rashi",
        "moon_details.sign",
        "moon.sign",
      ]) ?? "—",

    nakshatra:
      readPath(data, [
        "nakshatra_details.nakshatra",
        "nakshatra",
        "birth_star",
        "janma_nakshatra",
      ]) ?? "—",

    tithi:
      readPath(data, [
        "tithi",
        "tithi_details.tithi",
        "panchang.tithi",
      ]) ?? "—",

    yoga:
      readPath(data, [
        "yoga",
        "yoga_details.yoga",
        "panchang.yoga",
      ]) ?? "—",

    karana:
      readPath(data, [
        "karana",
        "karana_details.karana",
        "panchang.karana",
      ]) ?? "—",

    sunSign:
      readPath(data, [
        "sun_sign",
        "sunSign",
        "surya_rashi",
        "sun_details.sign",
        "sun.sign",
      ]) ?? "—",
  } as KundliResult;
}

function renderKundli(payload: unknown): void {
  const result = mapKundli(payload);
  const answer = $("answer");

  answer.className = "notice kundli-result";
  answer.hidden = false;

  answer.innerHTML = `
    <h3>वास्तविक वैदिक कुंडली</h3>
    <p>यह विवरण जन्म-समय और स्थान के आधार पर प्रदाता से प्राप्त हुआ है।</p>

    <div class="kundli-grid">
      <div class="kundli-item">
        <span class="kundli-item-label">जन्म स्थान</span>
        <strong>${result.birthPlace}</strong>
      </div>

      <div class="kundli-item">
        <span class="kundli-item-label">लग्न</span>
        <strong>${result.lagna}</strong>
      </div>

      <div class="kundli-item">
        <span class="kundli-item-label">चंद्र राशि</span>
        <strong>${result.moonSign}</strong>
      </div>

      <div class="kundli-item">
        <span class="kundli-item-label">नक्षत्र</span>
        <strong>${result.nakshatra}</strong>
      </div>

      <div class="kundli-item">
        <span class="kundli-item-label">तिथि</span>
        <strong>${result.tithi}</strong>
      </div>

      <div class="kundli-item">
        <span class="kundli-item-label">योग</span>
        <strong>${result.yoga}</strong>
      </div>

      <div class="kundli-item">
        <span class="kundli-item-label">करण</span>
        <strong>${result.karana}</strong>
      </div>

      <div class="kundli-item">
        <span class="kundli-item-label">सूर्य राशि</span>
        <strong>${result.sunSign}</strong>
      </div>
    </div>

    <details>
      <summary>पूरा प्रदाता डेटा देखें</summary>
      <pre class="kundli-json">${escapeHtml(
        JSON.stringify(payload, null, 2),
      )}</pre>
    </details>
  `;
}

function escapeHtml(value: string): string {
  return value.replace(
    /[&<>"']/g,
    (character) =>
      ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
      })[character] ?? character,
  );
}

async function getAccessToken(): Promise<string> {
  if (accessToken) {
    return accessToken;
  }

  if (!SUPABASE_ANON_KEY) {
    throw new Error("Supabase browser key is not configured in this build.");
  }

  const response = await fetch(`${SUPABASE_URL}/auth/v1/signup`, {
    method: "POST",
    headers: {
      apikey: SUPABASE_ANON_KEY,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({}),
  });

  if (!response.ok) {
    throw new Error(`Authentication failed (${response.status}).`);
  }

  const body = (await response.json()) as {
    access_token?: string;
  };

  if (!body.access_token) {
    throw new Error("Authentication did not return an access token.");
  }

  accessToken = body.access_token;

  return accessToken;
}

function renderRashis(): void {
  const grid = $("rashiGrid");

  grid.innerHTML = "";

  rashiList.forEach(
    (rashi: (typeof rashiList)[number], index: number) => {
      const button = document.createElement("button");

      button.type = "button";
      button.className = "rashi";
      button.setAttribute(
        "aria-pressed",
        String(rashi.id === selectedRashi.id),
      );

      button.innerHTML = `
        <span class="rashi-symbol">${rashi.symbol}</span>
        <span class="rashi-name">${rashi.names[locale]}</span>
        <span class="rashi-index">${index + 1} / 12</span>
      `;

      button.addEventListener("click", () => {
        selectedRashi = rashi;
        renderRashis();
        renderWeekly();
      });

      grid.appendChild(button);
    },
  );
}

function renderWeekly(): void {
  const content = runtime.getWeeklyHoroscope(selectedRashi.id, locale);

  $("selectedName").textContent = selectedRashi.names[locale];
  $("weeklyText").textContent = content;
  $("selectedRashiLabel").textContent =
    `${selectedRashi.names[locale]} — चयनित राशि`;
  $("selectedRashiHint").textContent =
    translations[locale].selectedRashiHint;
}

function bind(): void {
  $("language").addEventListener("change", (event) => {
    locale =
      localeMap[(event.target as HTMLSelectElement).value] ?? "hi-IN";

    renderRashis();
    renderWeekly();
  });

  $("birthForm").addEventListener("submit", async (event) => {
    event.preventDefault();

    const button = $("askButton") as HTMLButtonElement;
    const answer = $("answer");

    const birthDate = $("birthDate") as HTMLInputElement;
    const birthTime = $("birthTime") as HTMLInputElement;
    const latitudeInput = $("latitude") as HTMLInputElement;
    const longitudeInput = $("longitude") as HTMLInputElement;

    button.disabled = true;
    answer.hidden = false;
    answer.className = "notice";
    answer.textContent = "कुंडली डेटा प्राप्त किया जा रहा है…";

    try {
      const token = await getAccessToken();

      const date = birthDate.value;
      const time = birthTime.value;
      const latitude = latitudeInput.value;
      const longitude = longitudeInput.value;

      const response = await fetch(KUNDLI_ENDPOINT, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          datetime: `${date}T${time}:00+05:30`,
          coordinates: `${latitude},${longitude}`,
        }),
      });

      const payload = await response.json();

      if (!response.ok) {
        throw new Error(
          payload?.error ?? `Provider request failed (${response.status}).`,
        );
      }

      renderKundli(payload);
    } catch (error) {
      answer.className = "notice";
      answer.textContent =
        error instanceof Error
          ? error.message
          : "कुंडली डेटा प्राप्त नहीं हो सका।";
    } finally {
      button.disabled = false;
    }
  });

  renderRashis();
  renderWeekly();
}

bind();
