from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "docs/admanthan-dashboard/admanthan_browser.py"
gate = ROOT / "docs/admanthan-dashboard/semantic_fit_gate.py"
out = Path("/tmp/published-site/admanthan/admanthan_browser.py")

text = source.read_text(encoding="utf-8")
gate_text = gate.read_text(encoding="utf-8")
patch = r'''

# KALP AdManthan v0.8.9 runtime integration.
# Preserve the v0.8.8 selector and all of its shot-fit, necessity, no-padding
# and diversity protections. The semantic gate only removes incompatible
# library rows before the existing selector evaluates them.
_KALP_V088_CHOOSE_EFFECTS = choose_effects

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
        result["semantic_fit_version"] = VERSION
        result["semantic_fit_diagnostics"] = diagnostics
    return result
'''

out.write_text(text + "\n" + gate_text + patch, encoding="utf-8")
print(f"Wrote {out} ({out.stat().st_size} bytes)")
