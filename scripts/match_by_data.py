import sys
sys.stdout.reconfigure(encoding='utf-8')

import pyreadstat
import pandas as pd
import json
import re

# Load Aysen sav to see all original questions and labels
df_ays, meta_ays = pyreadstat.read_sav(r"C:\AGY\BAROMETRO\Base Barómetro Aysén 2025.03.11.sav")

# Load integrated sav
df_int, meta_int = pyreadstat.read_sav(r"C:\AGY\BAROMETRO\base_integrada_spss.sav")

# Let's inspect all columns of Aysen dataset
ays_vars = []
for c in df_ays.columns:
    lbl = meta_ays.column_names_to_labels.get(c, '')
    val_map = meta_ays.variable_value_labels.get(c, {})
    ays_vars.append({
        "col": c,
        "label": lbl,
        "val_map": {str(k): v for k, v in val_map.items()}
    })

print(f"Aysen has {len(ays_vars)} variables.")

# Now for each of the 67 columns in df_int, let's find the exact matching question in Aysen dataset
int_to_ays_mapping = []

for idx, icol in enumerate(df_int.columns):
    ival_map = meta_int.variable_value_labels.get(icol, {})
    
    # Try finding candidate matches in Aysen dataset
    candidates = []
    
    # We can match by:
    # 1. Identical / very similar value labels
    # 2. Variable label if present
    # 3. Correlation on Aysén subset (df_int[df_int['region_ord']==6] vs df_ays)
    
    # Aysen subset in integrated dataset:
    sub_int_ays = df_int[df_int['region_ord'] == 6.0][icol].reset_index(drop=True)
    
    best_match = None
    best_corr = -1
    best_match_label = ""
    
    # Check if there is exact or near 1.0 correlation with any Aysén column!
    for acol in df_ays.columns:
        sub_ays = df_ays[acol].reset_index(drop=True)
        # check if non-null counts match and values match
        try:
            # check numeric comparison
            s1 = pd.to_numeric(sub_int_ays, errors='coerce')
            s2 = pd.to_numeric(sub_ays, errors='coerce')
            
            # check match percentage
            valid_mask = s1.notnull() & s2.notnull()
            if valid_mask.sum() > 50:
                match_pct = (s1[valid_mask] == s2[valid_mask]).mean()
                if match_pct > 0.95:
                    best_match = acol
                    best_corr = match_pct
                    best_match_label = meta_ays.column_names_to_labels.get(acol, '')
                    break
        except Exception as e:
            pass
            
    int_to_ays_mapping.append({
        "int_col": icol,
        "num": idx + 1,
        "int_val_labels": {str(k): v for k, v in ival_map.items()},
        "matched_ays_col": best_match,
        "match_accuracy": best_corr,
        "ays_label": best_match_label
    })

with open(r"C:\AGY\BAROMETRO\scripts\int_to_ays_mapping.json", "w", encoding="utf-8") as f:
    json.dump(int_to_ays_mapping, f, ensure_ascii=False, indent=2)

print("\n--- MAPPING RESULTS ---")
for m in int_to_ays_mapping:
    print(f"[{m['num']:02d}] {m['int_col']:<25} -> {str(m['matched_ays_col']):<15} | {m['ays_label'][:60]}")
