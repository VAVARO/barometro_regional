import pyreadstat
import pandas as pd
import json

df, meta = pyreadstat.read_sav(r"C:\AGY\BAROMETRO\base_integrada_spss.sav")

print("=== CHECKING AGE ===")
print("Edad non-nulls by region:")
for r in sorted(df['region_ord'].unique()):
    sub = df[df['region_ord'] == r]['Edad_2019_2022_2024']
    print(f"Region {r}: non-null={sub.notnull().sum()}, mean={sub.dropna().mean():.1f}, min={sub.dropna().min()}, max={sub.dropna().max()}")

print("\n=== CHECKING LOS LAGOS IN P049..P057 ===")
sub_lagos = df[df['region_ord'] == 5.0]
for c in ['P049_2019_2022_2024', 'P050_2019_2022_2024', 'P051_2019_2022_2024', 'P059_2019_2022_2024']:
    print(f"{c}: non-null in Los Lagos = {sub_lagos[c].notnull().sum()} / {len(sub_lagos)}")

print("\n=== CHECKING NUBLE IN GSE ===")
sub_nuble = df[df['region_ord'] == 2.0]
print(f"GSE non-null in Ñuble = {sub_nuble['GSE_2019_2022_2024'].notnull().sum()} / {len(sub_nuble)}")

