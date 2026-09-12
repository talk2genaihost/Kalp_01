from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "admanthan-dashboard" / "admanthan_browser.py"
GATE = ROOT / "docs" / "admanthan-dashboard" / "semantic_fit_gate.py"
OUT = ROOT / "docs" / "admanthan-dashboard" / "admanthan_browser.py"

source = SOURCE.read_text(encoding="utf-8")
gate = GATE.read_text(encoding="utf-8")

if "0.8.8-effect-necessity-shot-fit" not in source:
    raise SystemExit("Expected v0.8.8 source baseline not found")
if 'def evaluate_effect(' not in gate:
    raise SystemExit("Semantic gate contract missing")
if 'def choose_effects(' not in source:
    raise SystemExit("choose_effects() missing from v0.8.8 source")

# Integrate the semantic gate directly into the published runtime.
# The v0.8.8 source is retained as the baseline; v0.8.9 replaces its
# choose_effects entry point with a DIRECT-only semantic prefilter, then
# delegates to the existing v0.8.8 shot-fit/necessity/diversity selector.
marker = "\ndef execute("
pos = source.find(marker)
if pos < 0:
    raise SystemExit("execute() insertion point not found")

prefix = source[:pos]
rest = source[pos:]

old_choose = "\n" + source[source.find("def choose_effects("):pos]
# Extract the existing function block by using the execute boundary.
choose_start = source.find("def choose_effects(")
if choose_start < 0 or choose_start >= pos:
    raise SystemExit("choose_effects block not found")
base_choose = source[choose_start:pos]

integration = f'''\n# KALP v0.8.9 — Semantic Production Fit Gate\n{gate}\n\n_KALP_V088_CHOOSE_EFFECTS = choose_effects\nKALP_V089_SEMANTIC_INTEGRATED = True\nVERSION = "0.8.9-semantic-production-fit"\n\n# Preserve v0.8.8 selection, but only after strict semantic DIRECT filtering.\ndef choose_effects(rows, scene, limit=3):\n    semantic_rows = []\n    diagnostics = []\n    counts = {{"DIRECT": 0, "SUPPORTING": 0, "INCOMPATIBLE": 0}}\n    for row in rows or []:\n        fit = evaluate_effect(scene, row)\n        diagnostics.append(fit)\n        state = fit.get("compatibility")\n        if state in counts:\n            counts[state] += 1\n        if state == "DIRECT":\n            semantic_rows.append(row)\n\n    result = _KALP_V088_CHOOSE_EFFECTS(semantic_rows, scene, limit)\n    result["semantic_fit_stage"] = "EXECUTED"\n    result["semantic_fit_version"] = VERSION\n    result["semantic_fit_counts"] = counts\n    result["semantic_fit_diagnostics"] = diagnostics\n    result["semantic_fit_direct_rows"] = len(semantic_rows)\n    return result\n'''

# Rebuild without the original choose_effects definition, then append the
# integrated v0.8.9 implementation before execute().
rebuilt = prefix[:choose_start] + integration + rest
OUT.write_text(rebuilt, encoding="utf-8")

check = OUT.read_text(encoding="utf-8")
required = [
    'VERSION = "0.8.9-semantic-production-fit"',
    'KALP_V089_SEMANTIC_INTEGRATED = True',
    'semantic_fit_stage',
    'semantic_fit_diagnostics',
    'if state == "DIRECT":',
    'def evaluate_effect(',
]
missing = [x for x in required if x not in check]
if missing:
    raise SystemExit("Build proof missing: " + ", ".join(missing))
print("Built", OUT)
