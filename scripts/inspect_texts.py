import re
import json

with open(r"C:\AGY\BAROMETRO\Diccionario de Variables - UAYSÉN. 2025.03.10_extracted.txt", "r", encoding="utf-8", errors="ignore") as f:
    dict_text = f.read()

with open(r"C:\AGY\BAROMETRO\documentos_barometros_regionales\barometro_Informe-Nacional-Barometro-2024_extracted.txt", "r", encoding="utf-8", errors="ignore") as f:
    nat_text = f.read()

with open(r"C:\AGY\BAROMETRO\Cuestionario Estudio Barómetro Regional Aysén_2024.12.27_v4_cambios post Pretest_extracted.txt", "r", encoding="utf-8", errors="ignore") as f:
    cuest_text = f.read()

# Let's inspect the exact lines in quest_text and nat_text
print("=== NATIONAL REPORT SAMPLE ===")
for line in nat_text.split('\n')[:80]:
    if line.strip():
        print(line[:100])

print("\n=== QUESTIONNAIRE SAMPLE ===")
for line in cuest_text.split('\n')[:100]:
    if line.strip():
        print(line[:100])
