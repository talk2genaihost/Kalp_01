from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "docs/admanthan-dashboard/admanthan_browser.py"
gate = ROOT / "docs/admanthan-dashboard/semantic_fit_gate.py"
out = Path("/tmp/published-site/admanthan/admanthan_browser.py")

text = source.read_text(encoding="utf-8")
gate_text = gate.read_text(encoding="utf-8")

# The v0.8.8 engine defines execute() after choose_effects(). The previous
# integration appended the semantic override after the whole source file.
# That made the published artifact look like v0.8.9 while execute() could
# still bind/use the pre-gate selector during runtime initialization.
# Integrate the gate immediately after the v0.8.8 selector and BEFORE execute().
marker = "\ndef execute("
idx = text.find(marker)
if idx < 0:
    raise RuntimeError("v0.8.9 integration marker not found: def execute(")

integration = r'''

# KALP AdManthan v0.8.9 runtime integration.
# Semantic Production Fit is intrinsic to the generated runtime and executes
# before the existing v0.8.8 shot-fit / necessity / diversity protections.
_KALP_V088_CHOOSE_EFFECTS = choose_effects

''' + gate_text + r'''

# v0.8.9 public runtime designation.
VERSION = "0.8.9-semantic-production-fit"


def choose_effects(rows, scene, limit=3):
    semantic_rows = []
    diagnostics = []
    for row in rows or []:
        fit = evaluate_effect(scene, row)
        diagnostics.append(fit)
        if fit.get("compatibility") != "INCOMPATIBLE":
            semantic_rows.append(row)

    result = _KALP_V088_CHOOSE_EFFECTS(semantic_rows, scene, limit)
    if isinstance(result, dict):
        result["semantic_fit_stage"] = "EXECUTED"
        result["semantic_fit_version"] = VERSION
        result["semantic_fit_diagnostics"] = diagnostics
        counts = {"DIRECT": 0, "SUPPORTING": 0, "INCOMPATIBLE": 0}
        for item in diagnostics:
            state = item.get("compatibility")
            if state in counts:
                counts[state] += 1
        result["semantic_fit_counts"] = counts
    return result
'''

out_text = text[:idx] + integration + text[idx:]
out.write_text(out_text, encoding="utf-8")

# Build-time proof: the published runtime must expose the semantic stage and
# diagnostics before the Pages artifact is accepted.
required = [
    'VERSION = "0.8.9-semantic-production-fit"',
    '"semantic_fit_stage"',
    '"semantic_fit_diagnostics"',
    '"semantic_fit_counts"',
    'stage": "SEMANTIC_FIT"',
]
missing = [x for x in required if x not in out_text]
if missing:
    raise RuntimeError("v0.8.9 integration proof failed: missing " + ", ".join(missing))

print(f"Wrote intrinsic v0.8.9 runtime ({out.stat().st_size} bytes)")
