const SUPABASE_URL = "https://cfwrgalgscieddkcrtde.supabase.co";
const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY as string | undefined;
const GATEWAY_ENDPOINT = `${SUPABASE_URL}/functions/v1/kalp-intelligence-gateway`;

interface Interpretation {
  summary?: string;
  personality?: string[];
  career?: string[];
  relationships?: string[];
  finance?: string[];
  dasha?: string[];
  nakshatra?: string[];
  yogas?: string[];
  strengths?: string[];
  cautions?: string[];
  focus?: string[];
  guidance?: string[];
}

function escapeHtml(value: string): string {
  return value.replace(/[&<>\"']/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[character] ?? character);
}

function asList(value: unknown): string[] {
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === "string" && item.trim().length > 0) : [];
}

function ensurePersonalFields(): void {
  const form = document.getElementById("birthForm");
  if (!form || form.querySelector("#birthName")) return;

  const grid = document.createElement("div");
  grid.className = "formgrid";
  grid.innerHTML = `
    <label>
      <span>नाम / Name</span>
      <input id="birthName" type="text" required autocomplete="name" placeholder="जैसे Gaurav">
    </label>
    <label>
      <span>लिंग / Sex</span>
      <select id="birthSex" required>
        <option value="">चुनें / Select</option>
        <option value="male">पुरुष / Male</option>
        <option value="female">महिला / Female</option>
        <option value="other">अन्य / Other</option>
      </select>
    </label>`;
  form.insertBefore(grid, form.firstElementChild);
}

async function getGatewayToken(): Promise<string> {
  if (!SUPABASE_ANON_KEY) throw new Error("KALP Gemini bridge is not configured in this build.");
  const response = await fetch(`${SUPABASE_URL}/auth/v1/signup`, {
    method: "POST",
    headers: { apikey: SUPABASE_ANON_KEY, "Content-Type": "application/json" },
    body: JSON.stringify({}),
  });
  if (!response.ok) throw new Error(`KALP Gateway authentication failed (${response.status}).`);
  const body = await response.json() as { access_token?: string };
  if (!body.access_token) throw new Error("KALP Gateway authentication did not return an access token.");
  return body.access_token;
}

async function interpret(payload: unknown): Promise<Interpretation> {
  const token = await getGatewayToken();
  const root = payload as Record<string, unknown>;
  const requested = root.requested ?? {};
  const data = root.data ?? {};
  const name = (document.getElementById("birthName") as HTMLInputElement | null)?.value.trim() ?? "";
  const sex = (document.getElementById("birthSex") as HTMLSelectElement | null)?.value ?? "";
  const prompt = [
    "You are the KALP Astro Rashi interpretation layer for a detailed Vedic astrology reading.",
    "Use only the supplied Vedic chart/provider facts. Never invent a planet, house, sign, nakshatra, yoga, dasha, degree, aspect, or placement that is not present in the supplied data.",
    "Explain what the supplied facts can reasonably indicate, and explicitly avoid overclaiming when data is missing.",
    "Use cautious, non-deterministic language such as 'संकेत मिलते हैं', 'संभावना हो सकती है', or 'यह प्रवृत्ति दिखाई देती है'. Do not present astrology as scientific certainty.",
    "Do not provide medical diagnosis/treatment, guaranteed predictions, legal advice, or guaranteed financial outcomes. For finance, discuss behavioral tendencies only, not investment instructions. For relationships, discuss communication and tendencies, not guaranteed events.",
    "Return JSON only with exactly these keys: summary (string), personality (string[]), career (string[]), relationships (string[]), finance (string[]), dasha (string[]), nakshatra (string[]), yogas (string[]), strengths (string[]), cautions (string[]), focus (string[]), guidance (string[]).",
    "Write all values in natural, conversational Hindi. Keep each bullet informative but concise. Aim for 2-4 bullets in each section when the supplied facts support it; otherwise return a shorter list.",
    "The reading should feel like a complete personal chart overview, not a generic zodiac horoscope.",
    `Person details: ${JSON.stringify({ name, sex })}`,
    `Requested birth context: ${JSON.stringify(requested)}`,
    `Full normalized provider data: ${JSON.stringify(data)}`,
  ].join("\n\n");

  const response = await fetch(GATEWAY_ENDPOINT, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      apikey: SUPABASE_ANON_KEY ?? "",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      provider: "gemini",
      gemini_models: ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-2.5-flash"],
      prompt,
    }),
  });
  const body = await response.json() as { output?: string; message?: string; attempts?: unknown[] };
  if (!response.ok || !body.output) {
    const detail = Array.isArray(body.attempts) && body.attempts.length ? ` ${body.attempts.map((attempt) => JSON.stringify(attempt)).join(" ")}` : "";
    throw new Error((body.message ?? `KALP Gemini request failed (${response.status}).`) + detail);
  }
  const parsed = JSON.parse(body.output) as Interpretation;
  return {
    summary: typeof parsed.summary === "string" ? parsed.summary : undefined,
    personality: asList(parsed.personality),
    career: asList(parsed.career),
    relationships: asList(parsed.relationships),
    finance: asList(parsed.finance),
    dasha: asList(parsed.dasha),
    nakshatra: asList(parsed.nakshatra),
    yogas: asList(parsed.yogas),
    strengths: asList(parsed.strengths),
    cautions: asList(parsed.cautions),
    focus: asList(parsed.focus),
    guidance: asList(parsed.guidance),
  };
}

function renderListSection(title: string, items: string[]): string {
  if (!items.length) return "";
  return `<div class="kalp-gemini-section"><h4>${escapeHtml(title)}</h4><ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul></div>`;
}

function renderInterpretation(value: Interpretation, answer: HTMLElement): void {
  const section = document.createElement("section");
  section.className = "kalp-gemini-interpretation";
  section.innerHTML = `
    <div class="kalp-gemini-header">
      <div><span class="kalp-gemini-eyebrow">KALP · Gemini</span><h3>विस्तृत वैदिक व्याख्या</h3></div>
      <span class="kalp-gemini-badge">AI Interpretation</span>
    </div>
    <p class="kalp-gemini-summary">${escapeHtml(value.summary ?? "इस चार्ट के लिए पर्याप्त व्याख्यात्मक तथ्य उपलब्ध नहीं हैं।")}</p>
    <div class="kalp-gemini-sections">
      ${renderListSection("व्यक्तित्व और स्वभाव", value.personality ?? [])}
      ${renderListSection("करियर और कार्यशैली", value.career ?? [])}
      ${renderListSection("रिश्ते और संचार", value.relationships ?? [])}
      ${renderListSection("धन और वित्तीय प्रवृत्तियाँ", value.finance ?? [])}
      ${renderListSection("दशा के संकेत", value.dasha ?? [])}
      ${renderListSection("नक्षत्र के संकेत", value.nakshatra ?? [])}
      ${renderListSection("योगों के संकेत", value.yogas ?? [])}
      ${renderListSection("मुख्य शक्तियाँ", value.strengths ?? [])}
      ${renderListSection("सावधानियाँ", value.cautions ?? [])}
      ${renderListSection("अभी ध्यान देने के क्षेत्र", value.focus ?? [])}
      ${renderListSection("व्यावहारिक मार्गदर्शन", value.guidance ?? [])}
    </div>
    <small>यह व्याख्या उपलब्ध वैदिक चार्ट डेटा पर आधारित AI interpretation है; इसे निश्चित भविष्यवाणी या पेशेवर सलाह न माना जाए।</small>`;
  const details = answer.querySelector(".kundli-result > details, details");
  if (details) answer.insertBefore(section, details);
  else answer.insertBefore(section, answer.firstChild);
}

function processKundliResult(answer: HTMLElement): void {
  if (answer.dataset.kalpGeminiProcessed === "true") return;
  const json = answer.querySelector(".kundli-json");
  if (!json) return;

  let payload: unknown;
  try {
    payload = JSON.parse(json.textContent ?? "{}");
  } catch {
    return;
  }

  answer.dataset.kalpGeminiProcessed = "true";
  const loading = document.createElement("section");
  loading.className = "kalp-gemini-interpretation kalp-gemini-loading";
  loading.innerHTML = `<h3>विस्तृत KALP Gemini व्याख्या</h3><p>चार्ट के उपलब्ध संकेतों का विस्तृत विश्लेषण तैयार किया जा रहा है…</p>`;
  const details = answer.querySelector("details");
  if (details) answer.insertBefore(loading, details);
  else answer.insertBefore(loading, answer.firstChild);

  void interpret(payload)
    .then((result) => {
      loading.remove();
      renderInterpretation(result, answer);
    })
    .catch((error) => {
      loading.innerHTML = `<h3>विस्तृत KALP Gemini व्याख्या</h3><p>${escapeHtml(error instanceof Error ? error.message : "KALP Gemini व्याख्या उपलब्ध नहीं है।")}</p>`;
    });
}

ensurePersonalFields();
const answer = document.getElementById("answer");
if (answer) {
  const observer = new MutationObserver(() => processKundliResult(answer));
  observer.observe(answer, { childList: true, subtree: true });
  processKundliResult(answer);
}
