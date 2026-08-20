import pyreadstat
import pandas as pd
import json

df, meta = pyreadstat.read_sav(r"C:\AGY\BAROMETRO\base_integrada_spss.sav")

# Let's inspect each question's val_labels and values
vars_detail = []
for i, col in enumerate(df.columns):
    lbl = meta.column_names_to_labels.get(col) or ""
    val_labels = meta.variable_value_labels.get(col, {})
    
    # Calculate non-nulls by region
    reg_valid = {}
    for r_val, r_name in [(1.0, "O'Higgins"), (2.0, "Ñuble"), (3.0, "Biobío"), (4.0, "Los Ríos"), (5.0, "Los Lagos"), (6.0, "Aysén"), (7.0, "Magallanes")]:
        sub = df[df['region_ord'] == r_val][col]
        reg_valid[r_name] = f"{sub.notnull().sum()}/{len(sub)}"
    
    val_counts = df[col].value_counts(dropna=True).to_dict()
    
    vars_detail.append({
        "num": i+1,
        "col": col,
        "label": lbl,
        "val_labels": val_labels,
        "reg_valid": reg_valid,
        "counts": {str(k): int(v) for k, v in val_counts.items()}
    })

# Save to json and print a clean table
with open(r"C:\AGY\BAROMETRO\scripts\vars_detail.json", "w", encoding="utf-8") as f:
    json.dump(vars_detail, f, ensure_ascii=False, indent=2)

for v in vars_detail:
    print(f"[{v['num']:02d}] {v['col']:<25} | {list(v['val_labels'].values())[:3]}")

