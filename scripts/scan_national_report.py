import sys
sys.stdout.reconfigure(encoding='utf-8')

import pyreadstat
import pandas as pd
import json
import re

# Load files
df_int, meta_int = pyreadstat.read_sav(r"C:\AGY\BAROMETRO\base_integrada_spss.sav")

with open(r"C:\AGY\BAROMETRO\documentos_barometros_regionales\barometro_Informe-Nacional-Barometro-2024_extracted.txt", "r", encoding="utf-8", errors="ignore") as f:
    nat_text = f.read()

with open(r"C:\AGY\BAROMETRO\Cuestionario Estudio Barómetro Regional Aysén_2024.12.27_v4_cambios post Pretest_extracted.txt", "r", encoding="utf-8", errors="ignore") as f:
    cuest_text = f.read()

with open(r"C:\AGY\BAROMETRO\Diccionario de Variables - UAYSÉN. 2025.03.10_extracted.txt", "r", encoding="utf-8", errors="ignore") as f:
    dict_text = f.read()

# Let's inspect all questions and find what each variable corresponds to
# In the national report:
print("--- NATIONAL REPORT PAGES / SECTIONS ---")
lines = nat_text.split('\n')
for i, line in enumerate(lines):
    if any(k in line.lower() for k in ['pregunta', 'gráfico', 'figura', 'tabla', 'módulo', 'pertenencia', 'confianza', 'descentraliz', 'evaluación', 'democracia', 'medios', 'afectad']):
        print(f"L{i}: {line[:120]}")

