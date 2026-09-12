from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "docs/admanthan-dashboard/admanthan_browser.py"
gate = ROOT / "docs/admanthan-dashboard/semantic_fit_gate.py"
out = Path("/tmp/published-site/admanthan/admanthan_browser.py")

text = source.read_text(encoding="utf-8")
gate_text = gate.read_text(encoding="utf-8")

# Integrate immediately before execute() so the generated runtime binds the
# semantic selector before the production engine can execute it.
marker = "\ndef execute("
idx = text.find(marker)
if idx < 0:
    raise RuntimeError("v0.8.9 integration marker not found: def execute(")

integration = r'''

# KALP AdManthan v0.8.9 intrinsic Semantic Production Fit integration.
# Pipeline:
#   600-library -> SEMANTIC_FIT(DIRECT only) -> v0.8.8 SHOT_FIT
#   -> NECESSITY -> DIVERSITY -> SELECT -> NO PADDING.
# SUPPORTING semantic fit is diagnostic-only and can NEVER enter the old
# selector, because doing so would allow v0.8.8 to promote a supporting match.
_KALP_V088_CHOOSE_EFFECTS = choose_effects

''' + gate_text + r'''

VERSION = "0.8.9-semantic-production-fit"
KALP_V089_SEMANTIC_INTEGRATED = True


def choose_effects(rows, scene, limit=3):
    semantic_rows = []
    diagnostics = []
    counts = {"DIRECT": 0, "SUPPORTING": 0, "INCOMPATIBLE": 0}

    for row in rows or []:
        fit = evaluate_effect(scene, row)
        diagnostics.append(fit)
        state = fit.get("compatibility")
        if state in counts:
            counts[state] += 1
        # v0.8.9 hard rule: only DIRECT semantic production fit proceeds to
        # the existing v0.8.8 shot-fit / necessity / diversity selector.
        if state == "DIRECT":
            semantic_rows.append(row)

    result = _KALP_V088_CHOOSE_EFFECTS(semantic_rows, scene, limit)
    result["semantic_fit_stage"] = "EXECUTED"
    result["semantic_fit_version"] = VERSION
    result["semantic_fit_counts"] = counts
    result["semantic_fit_diagnostics"] = diagnostics
    result["semantic_fit_direct_rows"] = len(semantic_rows)
    return result
'''

out_text = text[:idx] + integration + text[idx:]
out.write_text(out_text, encoding="utf-8")

# Build-time proof: fail the Pages build if the published runtime does not
# contain the intrinsic gate, DIRECT-only handoff, and required diagnostics.
required = [
    'VERSION = "0.8.9-semantic-production-fit"',
    'KALP_V089_SEMANTIC_INTEGRATED = True',
    'if state == "DIRECT":',
    '"semantic_fit_stage"',
    '"semantic_fit_version"',
    '"semantic_fit_counts"',
    '"semantic_fit_diagnostics"',
    'stage": "SEMANTIC_FIT"',
]
missing = [x for x in required if x not in out_text]
if missing:
    raise RuntimeError("v0.8.9 integration proof failed: missing " + ", ".join(missing))

print(f"Wrote intrinsic v0.8.9 DIRECT-only runtime ({out.stat().st_size} bytes)")
