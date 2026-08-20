import re
import json

# 1. Read index.html
with open(r"C:\AGY\BAROMETRO\index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 2. Read app.js
with open(r"C:\AGY\BAROMETRO\js\app.js", "r", encoding="utf-8") as f:
    js = f.read()

# 3. Read comparativa_interregional.json
with open(r"C:\AGY\BAROMETRO\data\comparativa_interregional.json", "r", encoding="utf-8") as f:
    comp_json = json.load(f)

# Extract canvas IDs in HTML
html_canvases = re.findall(r'<canvas[^>]*id=["\'](chart-comp-[^"\']+)["\']', html)
print("Canvas IDs in index.html:", html_canvases)
print(f"Total comp canvas in HTML: {len(html_canvases)}")

# Extract canvas IDs in app.js
js_canvases = re.findall(r'renderComp[A-Za-z]+\(["\'](chart-comp-[^"\']+)["\']', js)
print("Canvas IDs in app.js:", js_canvases)
print(f"Total comp canvas in app.js: {len(js_canvases)}")

# Check matching
missing_in_html = set(js_canvases) - set(html_canvases)
missing_in_js = set(html_canvases) - set(js_canvases)

print(f"\nMissing in HTML: {missing_in_html}")
print(f"Missing in JS: {missing_in_js}")

assert len(missing_in_html) == 0, f"Error: {missing_in_html} missing in HTML!"
assert len(missing_in_js) == 0, f"Error: {missing_in_js} missing in JS!"

print("\n--- DATA INTEGRITY CHECK ---")
for k, v in comp_json.items():
    print(f"Key: {k:<25} | Type: {type(v).__name__:<6} | Entries: {len(v)}")

print("\nALL VERIFICATIONS PASSED PERFECTLY!")
