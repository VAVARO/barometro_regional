import re
import json

with open(r"C:\AGY\BAROMETRO\index.html", "r", encoding="utf-8") as f:
    html = f.read()

with open(r"C:\AGY\BAROMETRO\js\app.js", "r", encoding="utf-8") as f:
    js = f.read()

with open(r"C:\AGY\BAROMETRO\data\comparativa_interregional.json", "r", encoding="utf-8") as f:
    comp_json = json.load(f)

# Extract canvas in comparativa section of HTML
comp_tab_html = re.search(r'<div id=["\']tab-content-comparativa["\'][^>]*>(.*?)</div>\s*</main>', html, re.DOTALL)
if comp_tab_html:
    comp_canvases_html = re.findall(r'<canvas[^>]*id=["\']([^"\']+)["\']', comp_tab_html.group(1))
else:
    comp_canvases_html = []

print("HTML Comparativa Canvas IDs:", comp_canvases_html)

# Extract canvas IDs referenced in updateComparativaPanel in app.js
panel_match = re.search(r'async function updateComparativaPanel\(\)\s*\{(.*?)\n\}', js, re.DOTALL)
if panel_match:
    panel_js = panel_match.group(1)
    js_canvases = re.findall(r'["\'](chart-comp-[^"\']+)["\']', panel_js)
else:
    js_canvases = []

print("JS referenced Canvas IDs:", js_canvases)

missing_in_html = set(js_canvases) - set(comp_canvases_html)
missing_in_js = set(comp_canvases_html) - set(js_canvases)

print("Missing in HTML:", missing_in_html)
print("Missing in JS:", missing_in_js)

assert len(missing_in_html) == 0
assert len(missing_in_js) == 0

print("Data keys:", list(comp_json.keys()))
print("Matriz servicios count:", len(comp_json.get("matriz_servicios", [])))
print("Dimensiones coyuntura keys:", list(comp_json.get("dimensiones_coyuntura", {}).keys()))

print("\n--- ALL CHECKS PASSED! ---")
