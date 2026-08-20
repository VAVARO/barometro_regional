import pyreadstat
import pandas as pd
import json

# 1. Load Integrated Dataset
df_int, meta_int = pyreadstat.read_sav(r"C:\AGY\BAROMETRO\base_integrada_spss.sav")

# 2. Load Aysen Dataset (which has rich labels)
df_aysen, meta_aysen = pyreadstat.read_sav(r"C:\AGY\BAROMETRO\Base Barómetro Aysén 2025.03.11.sav")

# 3. Create mapping of labels
regions_map = {
    1.0: "O'Higgins",
    2.0: "Ñuble",
    3.0: "Biobío",
    4.0: "Los Ríos",
    5.0: "Los Lagos",
    6.0: "Aysén",
    7.0: "Magallanes"
}

# Let's inspect Aysen variable labels vs Integrated variable names
aysen_labels = meta_aysen.column_names_to_labels
aysen_val_labels = meta_aysen.variable_value_labels

print(f"Integrated shape: {df_int.shape}")
print(f"Aysen shape: {df_aysen.shape}")

# Let's see how columns in df_int correlate or match with questions
analysis_list = []

for idx, col in enumerate(df_int.columns):
    lbl_int = meta_int.column_names_to_labels.get(col) or ""
    val_labels_int = meta_int.variable_value_labels.get(col, {})
    
    # Try finding matching label in Aysen dataset or from code
    # Clean col name like 'P003_2019_2022_2024' -> 'P3' or 'B1' etc.
    # Check completeness by region
    reg_coverage = {}
    for r_code, r_name in regions_map.items():
        sub = df_int[df_int['region_ord'] == r_code][col]
        non_null = int(sub.notnull().sum())
        total = len(sub)
        pct = round(non_null / total * 100, 1)
        reg_coverage[r_name] = {"n": non_null, "total": total, "pct": pct}
    
    # Check years / values
    val_counts = df_int[col].value_counts(dropna=False).head(10).to_dict()
    
    analysis_list.append({
        "index": idx + 1,
        "col": col,
        "label_int": lbl_int,
        "val_labels_int": {str(k): v for k, v in val_labels_int.items()},
        "reg_coverage": reg_coverage,
        "total_valid": int(df_int[col].notnull().sum()),
        "sample_vals": str(val_counts)
    })

with open(r"C:\AGY\BAROMETRO\scripts\integrated_vars_full.json", "w", encoding="utf-8") as f:
    json.dump(analysis_list, f, ensure_ascii=False, indent=2)

print("Saved detailed variable analysis to scripts/integrated_vars_full.json")
