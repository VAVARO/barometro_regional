import json
import re

with open(r"C:\AGY\BAROMETRO\index.html", "r", encoding="utf-8") as f:
    html = f.read()

with open(r"C:\AGY\BAROMETRO\js\app.js", "r", encoding="utf-8") as f:
    js = f.read()

with open(r"C:\AGY\BAROMETRO\data\comparativa_interregional.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Extract canvases in HTML
comp_section = re.search(r'<div id="tab-content-comparativa"[^>]*>(.*?)</div>\s*</main>', html, re.DOTALL)
html_canvases = re.findall(r'<canvas[^>]*id=["\'](chart-comp-[^"\']+)["\']', comp_section.group(1))

print(f"Total HTML canvases in Comparativa: {len(html_canvases)}")
for i, c in enumerate(html_canvases, 1):
    print(f"  {i:2d}. {c}")

# Extract canvases in JS (handling multiline formatting)
js_canvases = re.findall(r'renderComp(?:Bar|StackedBar)\s*\(\s*["\'](chart-comp-[^"\']+)["\']', js)
print(f"\nTotal JS canvases in Comparativa: {len(js_canvases)}")
for i, c in enumerate(js_canvases, 1):
    print(f"  {i:2d}. {c}")

missing_in_html = set(js_canvases) - set(html_canvases)
missing_in_js = set(html_canvases) - set(js_canvases)

print(f"\nMissing in HTML: {missing_in_html}")
print(f"Missing in JS: {missing_in_js}")

assert len(missing_in_html) == 0, f"Missing in HTML: {missing_in_html}"
assert len(missing_in_js) == 0, f"Missing in JS: {missing_in_js}"

print("\n--- JSON DATA STRUCTURE CHECK ---")
for main_key in ["coyuntura", "servicios", "descentralizacion", "cohesion"]:
    assert main_key in data, f"Key {main_key} missing in JSON!"
    print(f"\nCategory: {main_key.upper()} ({len(data[main_key])} metrics)")
    for subk, val in data[main_key].items():
        if isinstance(val, list):
            print(f"  - {subk:<26} -> list of {len(val)} items (first item: {val[0] if len(val)>0 else 'EMPTY!'})")
            assert len(val) > 0, f"Empty list for {subk}"

print("\n\n>>> ALL COMPARATIVA PIPELINE & CATALOG TESTS PASSED PERFECTLY! <<<")
