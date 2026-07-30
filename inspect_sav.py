import pyreadstat
import pandas as pd
import json

df, meta = pyreadstat.read_sav('Base Barómetro Aysén 2025.03.11.sav')

print(f"Total Rows (N): {len(df)}")
print(f"Total Columns: {len(df.columns)}")

info = {}
info["columns"] = meta.column_names
info["labels"] = meta.column_names_to_labels
info["value_labels"] = meta.variable_value_labels

# Print key demographic columns and survey metrics
print("\n--- Demographics / Filter columns ---")
for col in meta.column_names:
    lbl = meta.column_names_to_labels.get(col, '')
    if any(k in col.upper() for k in ['COMUNA', 'ZONA', 'TRAMO', 'EDAD', 'GSE', 'SEXO', 'POND', 'PESO', 'W']):
        print(f"Col: {col:<15} Label: {lbl}")
        val_map = meta.variable_value_labels.get(col, {})
        print(f"   Values: {val_map}")

print("\n--- All Variables Overview ---")
for col in meta.column_names:
    lbl = meta.column_names_to_labels.get(col, '')
    print(f"{col:<15} | {lbl}")

with open('sav_metadata.json', 'w', encoding='utf-8') as f:
    json.dump({
        "column_names": meta.column_names,
        "column_labels": meta.column_names_to_labels,
        "value_labels": meta.variable_value_labels
    }, f, ensure_ascii=False, indent=2)
