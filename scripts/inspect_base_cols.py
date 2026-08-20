import pyreadstat
import json

df, meta = pyreadstat.read_sav(r"C:\AGY\BAROMETRO\base_integrada_spss.sav", encoding="latin1")
print("Columns:", list(df.columns))
print("region_ord values:", df['region_ord'].value_counts().to_dict())
print("Ponderador summary:", df['PonderadorRegional_2019_2022_2024'].describe().to_dict())
