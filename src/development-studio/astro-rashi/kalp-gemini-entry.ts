const SUPABASE_URL = "https://cfwrgalgscieddkcrtde.supabase.co";
const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY as string | undefined;
const GATEWAY_ENDPOINT = `${SUPABASE_URL}/functions/v1/kalp-intelligence-gateway`;

interface Interpretation {
  summary?: string;
  strengths?: string[];
  cautions?: string[];
  focus?: string[];
}

function escapeHtml(value: string): string {
  return value.replace(/[&<>\"']/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[character] ?? character);
}

function asList(value: unknown): string[] {
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === "string" && item.trim().length > 0) : [];
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
  const prompt = [
    "You are the KALP Astro Rashi interpretation layer.",
    "Interpret only the supplied Vedic chart facts; never invent missing placements.",
    "Use cautious, non-deterministic language. This is an interpretive reading, not medical, financial, legal, or guaranteed predictive advice.",
    "Return JSON only with keys: summary (string), strengths (string[]), cautions (string[]), focus (string[]).",
    "Write the response in conversational Hindi.",
    `Requested birth context: ${JSON.stringify(requested)}`,
    `Normalized provider data: ${JSON.stringify(data)}`,
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
      gemini_models: ["gemini-3.7-flash", "gemini-2.5-flash"],
      prompt,
    }),
  });
  const body = await response.json() as { output?: string; message?: string };
  if (!response.ok || !body.output) throw new Error(body.message ?? `KALP Gemini request failed (${response.status}).`);
  const parsed = JSON.parse(body.output) as Interpretation;
  return {
    summary: typeof parsed.summary === "string" ? parsed.summary : undefined,
    strengths: asList(parsed.strengths),
    cautions: asList(parsed.cautions),
    focus: asList(parsed.focus),
  };
}

function renderInterpretation(value: Interpretation): void {
  const answer = document.getElementById("answer");
  if (!answer) return;
  const section = document.createElement("section");
  section.className = "kalp-gemini-interpretation";
  section.innerHTML = `
    <h3>KALP Gemini व्याख्या</h3>
    <p>${escapeHtml(value.summary ?? "इस चार्ट के लिए पर्याप्त व्याख्यात्मक तथ्य उपलब्ध नहीं हैं।")}</p>
    ${value.strengths?.length ? `<strong>मुख्य संकेत</strong><ul>${value.strengths.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>` : ""}
    ${value.cautions?.length ? `<strong>सावधानियाँ</strong><ul>${value.cautions.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>` : ""}
    ${value.focus?.length ? `<strong>ध्यान के क्षेत्र</strong><ul>${value.focus.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>` : ""}
    <small>AI interpretation via KALP Intelligence Gateway · Gemini</small>`;
  answer.appendChild(section);
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
  const loading = document.createElement("p");
  loading.className = "kalp-gemini-loading";
  loading.textContent = "KALP Gemini व्याख्या तैयार की जा रही है…";
  answer.appendChild(loading);

  void interpret(payload)
    .then((result) => {
      loading.remove();
      renderInterpretation(result);
    })
    .catch((error) => {
      loading.textContent = error instanceof Error ? error.message : "KALP Gemini व्याख्या उपलब्ध नहीं है।";
    });
}

const answer = document.getElementById("answer");
if (answer) {
  const observer = new MutationObserver(() => processKundliResult(answer));
  observer.observe(answer, { childList: true, subtree: true });
  processKundliResult(answer);
}
