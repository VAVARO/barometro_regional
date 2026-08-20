import sys
sys.stdout.reconfigure(encoding='utf-8')

import pyreadstat
import pandas as pd
import json

df_int, meta_int = pyreadstat.read_sav(r"C:\AGY\BAROMETRO\base_integrada_spss.sav")
df_ays, meta_ays = pyreadstat.read_sav(r"C:\AGY\BAROMETRO\Base Barómetro Aysén 2025.03.11.sav")

unmatched = [
    'P004_2019_2022_2024',
    'P007_2019_2022_2024',
    'P022_2024',
    'P040_2024',
    'P041_2019_2022_2024',
    'P042_2019_2022_2024',
    'P043_2019_2022_2024',
    'P044_2019_2022_2024',
    'P045_2019_2022_2024',
    'P046_2019_2022_2024',
    'P047_2024',
    'P048_2019_2022_2024',
    'P059_2019_2022_2024',
    'P073_2019_2022_2024',
    'P074_2019_2022_2024'
]

print("=== UNMATCHED VARIABLES DETAILS ===")
for col in unmatched:
    val_lbls = meta_int.variable_value_labels.get(col, {})
    sample = df_int[col].value_counts(dropna=False).head(10).to_dict()
    print(f"\n--- {col} ---")
    print(f"Value labels: {val_lbls}")
    print(f"Counts: {sample}")

# Let's inspect Aysén questions for G2, G3, H1, H2, F3, F4, etc.
print("\n=== AYSEN COLS LIKE F, G, H ===")
for c in df_ays.columns:
    if any(c.startswith(k) for k in ['F', 'G', 'H', 'B2', 'C2', 'E', 'D']):
        lbl = meta_ays.column_names_to_labels.get(c, '')
        vl = meta_ays.variable_value_labels.get(c, {})
        print(f"{c:<15} | {lbl[:60]:<60} | {list(vl.values())[:3]}")

