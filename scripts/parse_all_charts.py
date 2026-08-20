import sys
sys.stdout.reconfigure(encoding='utf-8')

import re
import json

with open(r"C:\AGY\BAROMETRO\index.html", "r", encoding="utf-8") as f:
    html = f.read()

with open(r"C:\AGY\BAROMETRO\js\app.js", "r", encoding="utf-8") as f:
    js = f.read()

# Let's parse each tab and card in index.html with precision
tabs_info = [
    {"id": "resumen", "name": "1. Resumen Ejecutivo"},
    {"id": "identidad", "name": "2. Identidad & Pertenencia"},
    {"id": "gobernanza", "name": "3. Descentralización & Gobernanza"},
    {"id": "medioambiente", "name": "4. Medioambiente & Futuro"},
    {"id": "uaysen", "name": "5. UAysén en el Territorio"},
    {"id": "confianza", "name": "6. Confianza & Cohesión Social"},
    {"id": "demografia", "name": "7. Perfil Demográfico & Laboral"},
    {"id": "explorer", "name": "8. Data Intelligence (Explorer)"},
    {"id": "comparativa", "name": "9. Comparativa Interregional"}
]

chart_details = []

# Scan for each canvas in the document
canvas_matches = list(re.finditer(r'<canvas[^>]*id=["\']([^"\']+)["\'][^>]*>', html))

for m in canvas_matches:
    cid = m.group(1)
    pos = m.start()
    
    # Identify tab
    tab_before = html[:pos]
    tab_m = list(re.finditer(r'id=["\']tab-content-([^"\']+)["\']', tab_before))
    current_tab = tab_m[-1].group(1) if tab_m else "global"
    
    # Get card snippet
    snippet = html[max(0, pos - 700):pos + 100]
    
    # Find all h3, h4, p
    h3_tags = re.findall(r'<h3[^>]*>(.*?)</h3>', snippet, re.DOTALL)
    h4_tags = re.findall(r'<h4[^>]*>(.*?)</h4>', snippet, re.DOTALL)
    
    badge = re.sub(r'<[^>]+>', '', h3_tags[-1]).strip() if h3_tags else ""
    title = re.sub(r'<[^>]+>', '', h4_tags[-1]).strip() if h4_tags else ""
    
    chart_details.append({
        "tab": current_tab,
        "canvas_id": cid,
        "badge": badge,
        "title": title
    })

print(f"Total charts extracted: {len(chart_details)}")
with open(r"C:\AGY\BAROMETRO\scripts\all_charts_detailed.json", "w", encoding="utf-8") as f:
    json.dump(chart_details, f, ensure_ascii=False, indent=2)

