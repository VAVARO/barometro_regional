import re
import json

with open(r"C:\AGY\BAROMETRO\documentos_barometros_regionales\barometro_Informe-Nacional-Barometro-2024_extracted.txt", "r", encoding="utf-8", errors="ignore") as f:
    nat_text = f.read()

with open(r"C:\AGY\BAROMETRO\Diccionario de Variables - UAYSÉN. 2025.03.10_extracted.txt", "r", encoding="utf-8", errors="ignore") as f:
    dict_text = f.read()

with open(r"C:\AGY\BAROMETRO\Cuestionario Estudio Barómetro Regional Aysén_2024.12.27_v4_cambios post Pretest_extracted.txt", "r", encoding="utf-8", errors="ignore") as f:
    quest_text = f.read()

with open(r"C:\AGY\BAROMETRO\scripts\vars_detail.json", "r", encoding="utf-8") as f:
    vars_detail = json.load(f)

# Let's inspect each variable and find its exact question text from the dictionary / national report / questionnaire
results = []
for v in vars_detail:
    col = v['col']
    # Extract base number e.g. P003 -> P3 or P03 or P003
    m = re.match(r'P(\d+)', col)
    base_num = int(m.group(1)) if m else None
    
    # Let's look up in dict_text and quest_text
    info = {"col": col, "num": v['num'], "val_labels": v['val_labels'], "reg_valid": v['reg_valid']}
    results.append(info)

print(f"Total variables: {len(results)}")
