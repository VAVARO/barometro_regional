import pyreadstat
import pandas as pd
import openpyxl
import json
import os

print("=== 1. ANALYZING SPSS FILE ===")
sav_path = r"C:\AGY\BAROMETRO\base_integrada_spss.sav"
df_sav, meta_sav = pyreadstat.read_sav(sav_path)
print(f"SPSS Shape: {df_sav.shape}")
print(f"Total Columns: {len(df_sav.columns)}")

print("\nVariables and Labels in SPSS:")
for i, col in enumerate(df_sav.columns):
    lbl = meta_sav.column_names_to_labels.get(col) or ''
    val_labels = meta_sav.variable_value_labels.get(col, {})
    val_sample = str(val_labels)[:80] if val_labels else "No val labels"
    print(f"[{i+1:02d}] {col:<15} | {lbl[:60]:<60} | {val_sample}")

print("\n=== 2. ANALYZING EXCEL FILE ===")
xlsx_path = r"C:\AGY\BAROMETRO\base_integrada_excel.xlsx"
excel_file = pd.ExcelFile(xlsx_path)
print("Excel Sheet Names:", excel_file.sheet_names)
for sheet in excel_file.sheet_names:
    df_sheet = pd.read_excel(xlsx_path, sheet_name=sheet)
    print(f"Sheet '{sheet}' Shape: {df_sheet.shape}")
    print(f"Sheet '{sheet}' Columns (first 10):", df_sheet.columns.tolist()[:10])

print("\n=== 3. REGIONS / CASES IN SPSS ===")
region_cols = [c for c in df_sav.columns if any(k in c.upper() for k in ['REG', 'REGION', 'ZONA', 'CIUDAD', 'TERRITORIO', 'BASE', 'ESTUDIO'])]
print("Potential Region Columns in SPSS:", region_cols)
for c in region_cols:
    print(f"\nValue counts for column '{c}':")
    val_map = meta_sav.variable_value_labels.get(c, {})
    counts = df_sav[c].value_counts(dropna=False)
    for val, count in counts.items():
        label = val_map.get(val, "sin etiqueta")
        print(f"  {val} ({label}): {count}")

# Save metadata to json for detailed analysis
meta_dict = {
    "columns": df_sav.columns.tolist(),
    "labels": {k: (v if v is not None else "") for k, v in meta_sav.column_names_to_labels.items()},
    "value_labels": meta_sav.variable_value_labels,
    "shape": list(df_sav.shape)
}
with open(r"C:\AGY\BAROMETRO\scripts\integrated_meta.json", "w", encoding="utf-8") as f:
    json.dump(meta_dict, f, ensure_ascii=False, indent=2)
print("\nSaved metadata to integrated_meta.json")
