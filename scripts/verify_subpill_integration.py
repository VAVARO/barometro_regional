import json
import re

with open(r"C:\AGY\BAROMETRO\index.html", "r", encoding="utf-8") as f:
    html = f.read()

with open(r"C:\AGY\BAROMETRO\js\app.js", "r", encoding="utf-8") as f:
    js = f.read()

with open(r"C:\AGY\BAROMETRO\data\comparativa_interregional.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Extract canvas IDs inside tab-content-comparativa
comp_section = re.search(r'<div id="tab-content-comparativa"[^>]*>(.*?)</div>\s*</main>', html, re.DOTALL)
html_canvases = re.findall(r'<canvas[^>]*id=["\'](chart-comp-[^"\']+)["\']', comp_section.group(1))

print("Canvas IDs in index.html comparativa:", html_canvases)
print(f"Total: {len(html_canvases)}")

# Extract canvas IDs in app.js under renderActiveCompSubpanel
js_canvases = re.findall(r'renderComp(?:Bar|DualBar)\(["\'](chart-comp-[^"\']+)["\']', js)
print("Canvas IDs in js/app.js:", js_canvases)
print(f"Total: {len(js_canvases)}")

missing_in_html = set(js_canvases) - set(html_canvases)
missing_in_js = set(html_canvases) - set(js_canvases)

print(f"Missing in HTML: {missing_in_html}")
print(f"Missing in JS: {missing_in_js}")

assert len(missing_in_html) == 0, f"Missing in HTML: {missing_in_html}"
assert len(missing_in_js) == 0, f"Missing in JS: {missing_in_js}"

print("\n--- JSON DATA STRUCTURE CHECK ---")
for main_key in ["ficha_tecnica", "coyuntura", "servicios", "cohesion", "descentralizacion"]:
    assert main_key in data, f"Key {main_key} missing in JSON!"
    print(f"Key: {main_key:<18} -> {list(data[main_key].keys()) if isinstance(data[main_key], dict) else f'List of {len(data[main_key])} items'}")

print("\nALL SUB-PILL INTEGRATION CHECKS PASSED!")
