import sys
sys.stdout.reconfigure(encoding='utf-8')

import pyreadstat
import pandas as pd
import json
import re

df, meta = pyreadstat.read_sav(r"C:\AGY\BAROMETRO\base_integrada_spss.sav")

with open(r"C:\AGY\BAROMETRO\Diccionario de Variables - UAYSÉN. 2025.03.10_extracted.txt", "r", encoding="utf-8", errors="ignore") as f:
    dict_text = f.read()

with open(r"C:\AGY\BAROMETRO\Cuestionario Estudio Barómetro Regional Aysén_2024.12.27_v4_cambios post Pretest_extracted.txt", "r", encoding="utf-8", errors="ignore") as f:
    cuest_text = f.read()

# Let's parse the dictionary text
# Find sections like Variable, Pregunta, Categorias
print("=== SAMPLE DICTIONARY ENTRIES ===")
dict_blocks = re.split(r'\n(?=[A-Z0-9_]+\s*\n|\bVariable:|\bP\d+)', dict_text)
print(f"Total blocks in dict: {len(dict_blocks)}")

# Let's search for each P-variable in the questionnaire text
print("\n=== MATCHING QUESTIONNAIRE QUESTIONS ===")
cuest_lines = cuest_text.split('\n')
for i, line in enumerate(cuest_lines):
    if re.match(r'^(P\d+|[A-Z]\d+)\b', line.strip()):
        print(f"L{i}: {line[:100]}")
        # print next 3 lines
        for j in range(1, 4):
            if i + j < len(cuest_lines):
                print(f"   {cuest_lines[i+j][:100]}")

