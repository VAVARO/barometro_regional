import pyreadstat
import pandas as pd
import json

sav_path = r"C:\AGY\BAROMETRO\base_integrada_spss.sav"
df, meta = pyreadstat.read_sav(sav_path)

# Let's inspect each variable: its name, label, value labels, null count by region, etc.
var_summary = []

regions = {
    1.0: "O'Higgins",
    2.0: "Ñuble",
    3.0: "Biobío",
    4.0: "Los Ríos",
    5.0: "Los Lagos",
    6.0: "Aysén",
    7.0: "Magallanes"
}

reg_col = [c for c in df.columns if 'reg' in c.lower() and 'ord' not in c.lower()][0]
print(f"Region column identified: {reg_col}")

for col in df.columns:
    lbl = meta.column_names_to_labels.get(col) or ''
    val_map = meta.variable_value_labels.get(col, {})
    
    # Check completeness per region
    reg_counts = {}
    for r_code, r_name in regions.items():
        sub = df[df[reg_col] == r_code][col]
        non_null = sub.notnull().sum()
        total = len(sub)
        reg_counts[r_name] = f"{non_null}/{total}"
    
    unique_vals = df[col].dropna().unique()
    
    var_summary.append({
        "col": col,
        "label": lbl,
        "val_labels": {str(k): v for k, v in val_map.items()},
        "num_unique": len(unique_vals),
        "sample_values": sorted([float(x) for x in unique_vals if isinstance(x, (int, float))])[:10],
        "non_null_by_region": reg_counts,
        "total_non_null": int(df[col].notnull().sum())
    })

with open(r"C:\AGY\BAROMETRO\scripts\detailed_vars.json", "w", encoding="utf-8") as f:
    json.dump(var_summary, f, ensure_ascii=False, indent=2)

print(f"Saved {len(var_summary)} variables to scripts/detailed_vars.json")
