import json
import pyreadstat
import pandas as pd

# Load Aysen metadata
df_aysen, meta_aysen = pyreadstat.read_sav(r"C:\AGY\BAROMETRO\Base Barómetro Aysén 2025.03.11.sav")

# Load integrated
df_int, meta_int = pyreadstat.read_sav(r"C:\AGY\BAROMETRO\base_integrada_spss.sav")

# Let's match variables by inspecting labels and questions
# Let's print out the exact values and labels for each of the 67 columns in df_int
print(f"{'#':<3} | {'Variable':<25} | {'Val Labels':<40} | {'Aysen Match / Content'}")
print("-" * 100)

for i, col in enumerate(df_int.columns):
    val_lbls = meta_int.variable_value_labels.get(col, {})
    val_str = ", ".join([f"{k}:{v}" for k, v in list(val_lbls.items())[:3]])
    if len(val_lbls) > 3:
        val_str += "..."
    
    # Try to find corresponding variable in Aysen
    matched = []
    # Test column name prefixes
    for acol in df_aysen.columns:
        albl = meta_aysen.column_names_to_labels.get(acol, '')
        aval_lbls = meta_aysen.variable_value_labels.get(acol, {})
        # check if value labels or names match
        if acol.lower() in col.lower() or col.split('_')[0].lower() == acol.lower():
            matched.append(f"{acol}: {albl}")
    
    match_str = matched[0] if matched else "No direct name match"
    print(f"{i+1:<3} | {col:<25} | {val_str[:40]:<40} | {match_str[:50]}")

