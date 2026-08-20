import pyreadstat
import pandas as pd
import json

sav_path = r"C:\AGY\BAROMETRO\base_integrada_spss.sav"
df, meta = pyreadstat.read_sav(sav_path)

print("Exact columns in SPSS:")
for i, c in enumerate(df.columns):
    print(f"{i}: {repr(c)}")

# Check region_ord and Regi...
print("Value counts of region_ord:")
print(df['region_ord'].value_counts(dropna=False))

# Let's inspect the excel file as well
xlsx_path = r"C:\AGY\BAROMETRO\base_integrada_excel.xlsx"
df_xl = pd.read_excel(xlsx_path)
print("\nExact columns in Excel:")
for i, c in enumerate(df_xl.columns):
    print(f"{i}: {repr(c)}")
