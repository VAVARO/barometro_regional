import pyreadstat
import pandas as pd
import json
import re

# Load SPSS integrated dataset
df, meta = pyreadstat.read_sav(r"C:\AGY\BAROMETRO\base_integrada_spss.sav")

# Load dictionary text & questionnaire text
with open(r"C:\AGY\BAROMETRO\Diccionario de Variables - UAYSÉN. 2025.03.10_extracted.txt", "r", encoding="utf-8", errors="ignore") as f:
    dict_txt = f.read()

with open(r"C:\AGY\BAROMETRO\documentos_barometros_regionales\barometro_Informe-Nacional-Barometro-2024_extracted.txt", "r", encoding="utf-8", errors="ignore") as f:
    inf_nac_txt = f.read()

with open(r"C:\AGY\BAROMETRO\Cuestionario Estudio Barómetro Regional Aysén_2024.12.27_v4_cambios post Pretest_extracted.txt", "r", encoding="utf-8", errors="ignore") as f:
    cuest_txt = f.read()

# Load current app comparativa json
with open(r"C:\AGY\BAROMETRO\data\comparativa_interregional.json", "r", encoding="utf-8") as f:
    current_comp = json.load(f)

print("Current comparative keys in app:", list(current_comp.keys()))

regions_map = {
    1.0: "O'Higgins",
    2.0: "Ñuble",
    3.0: "Biobío",
    4.0: "Los Ríos",
    5.0: "Los Lagos",
    6.0: "Aysén",
    7.0: "Magallanes"
}

# Variable Catalog & Detailed Analysis
catalog = []

for idx, col in enumerate(df.columns):
    lbl = meta.column_names_to_labels.get(col) or ""
    val_labels = meta.variable_value_labels.get(col, {})
    
    # Regional coverage
    reg_stats = {}
    for r_code, r_name in regions_map.items():
        sub = df[df['region_ord'] == r_code]
        sub_valid = sub[col].dropna()
        n_valid = len(sub_valid)
        n_total = len(sub)
        pct_valid = round(n_valid / n_total * 100, 1)
        
        # Calculate distribution or mean
        # Check if score variable (values 1 to 7)
        unique_vals = sorted(sub_valid.unique())
        
        reg_stats[r_name] = {
            "n_valid": n_valid,
            "n_total": n_total,
            "pct_valid": pct_valid
        }
    
    total_valid = int(df[col].notnull().sum())
    total_records = len(df)
    
    catalog.append({
        "index": idx + 1,
        "col_name": col,
        "label": lbl,
        "val_labels": {str(k): v for k, v in val_labels.items()},
        "total_valid": total_valid,
        "total_pct": round(total_valid / total_records * 100, 1),
        "reg_stats": reg_stats
    })

with open(r"C:\AGY\BAROMETRO\scripts\complete_catalog.json", "w", encoding="utf-8") as f:
    json.dump(catalog, f, ensure_ascii=False, indent=2)

print("Complete catalog saved to scripts/complete_catalog.json")
