import sys
sys.stdout.reconfigure(encoding='utf-8')

import pyreadstat
import pandas as pd
import json

df, meta = pyreadstat.read_sav(r"C:\AGY\BAROMETRO\base_integrada_spss.sav")

with open(r"C:\AGY\BAROMETRO\Diccionario de Variables - UAYSÉN. 2025.03.10_extracted.txt", "r", encoding="utf-8", errors="ignore") as f:
    dict_text = f.read()

# Current app charts
with open(r"C:\AGY\BAROMETRO\data\comparativa_interregional.json", "r", encoding="utf-8") as f:
    curr_comp = json.load(f)

print("Current app comparativa keys:", list(curr_comp.keys()))

# Let's inspect each variable
var_audit = []

for i, col in enumerate(df.columns):
    lbl = meta.column_names_to_labels.get(col) or ""
    v_labels = meta.variable_value_labels.get(col, {})
    
    # Calculate weighted / unweighted distributions per region
    reg_data = {}
    for r_code, r_name in [(1.0, "O'Higgins"), (2.0, "Ñuble"), (3.0, "Biobío"), (4.0, "Los Ríos"), (5.0, "Los Lagos"), (6.0, "Aysén"), (7.0, "Magallanes")]:
        sub = df[df['region_ord'] == r_code]
        valid_sub = sub[col].dropna()
        n_valid = len(valid_sub)
        n_total = len(sub)
        reg_data[r_name] = {
            "n": n_valid,
            "total": n_total,
            "pct_valid": round(n_valid / n_total * 100, 1)
        }
    
    # Let's check unique values
    u_vals = sorted(df[col].dropna().unique().tolist())
    
    var_audit.append({
        "num": i + 1,
        "col": col,
        "label": lbl,
        "value_labels": {str(k): v for k, v in v_labels.items()},
        "unique_vals": u_vals[:15],
        "reg_data": reg_data
    })

with open(r"C:\AGY\BAROMETRO\scripts\var_audit_full.json", "w", encoding="utf-8") as f:
    json.dump(var_audit, f, ensure_ascii=False, indent=2)

print(f"Audited {len(var_audit)} variables. Full dump in scripts/var_audit_full.json")
