import sys
sys.stdout.reconfigure(encoding='utf-8')

import re
import json

with open(r"C:\AGY\BAROMETRO\index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Let's find all tab sections in index.html
tabs = re.findall(r'<div id=["\']tab-content-([^"\']+)["\'][^>]*>(.*?)</div>\s*<!--\s*SECTION|</div>\s*</main>', html, re.DOTALL)

print(f"Found {len(tabs)} tabs in index.html:")

chart_inventory = []

# Scan for each canvas in the document and find its surrounding card, title, subtitle, tab
canvas_matches = re.finditer(r'<canvas[^>]*id=["\']([^"\']+)["\'][^>]*>', html)

for m in canvas_matches:
    canvas_id = m.group(1)
    pos = m.start()
    
    # Find enclosing tab
    tab_before = html[:pos]
    tab_matches = list(re.finditer(r'id=["\']tab-content-([^"\']+)["\']', tab_before))
    tab_name = tab_matches[-1].group(1) if tab_matches else "global"
    
    # Find enclosing card (around 500 chars before canvas)
    snippet = html[max(0, pos - 600):pos + 200]
    
    # Extract h3, h4, or titles
    h3_m = re.findall(r'<h3[^>]*>(.*?)</h3>', snippet, re.DOTALL)
    h4_m = re.findall(r'<h4[^>]*>(.*?)</h4>', snippet, re.DOTALL)
    
    badge = h3_m[-1].strip() if h3_m else ""
    title = h4_m[-1].strip() if h4_m else ""
    
    # clean HTML tags
    badge = re.sub(r'<[^>]+>', '', badge).strip()
    title = re.sub(r'<[^>]+>', '', title).strip()
    
    chart_inventory.append({
        "tab": tab_name,
        "canvas_id": canvas_id,
        "badge": badge,
        "title": title
    })

print(f"Total canvas found: {len(chart_inventory)}")
with open(r"C:\AGY\BAROMETRO\scripts\chart_inventory.json", "w", encoding="utf-8") as f:
    json.dump(chart_inventory, f, ensure_ascii=False, indent=2)

for c in chart_inventory:
    print(f"[{c['tab']:<15}] {c['canvas_id']:<30} | {c['badge']:<25} | {c['title']}")

