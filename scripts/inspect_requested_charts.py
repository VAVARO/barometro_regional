import sys
sys.stdout.reconfigure(encoding='utf-8')

import pyreadstat
import pandas as pd
import numpy as np
import json

df, meta = pyreadstat.read_sav(r"C:\AGY\BAROMETRO\base_integrada_spss.sav")

regions = {
    1.0: "O'Higgins",
    2.0: "Ñuble",
    3.0: "Biobío",
    4.0: "Los Ríos",
    5.0: "Los Lagos",
    6.0: "Aysén",
    7.0: "Magallanes"
}

# The 9 requested variables:
# 1. Territorio de pertenencia: P001_2019_2022_2024
# 2. Rumbo regional completo: P003_2019_2022_2024
# 3. Principal problema de la región: P004_2019_2022_2024
# 4. Principal fortaleza percibida: P038_2019_2022_2024
# 5. Apoyo a la Democracia: P073_2019_2022_2024
# 6. Autoidentificación Política: P074_2019_2022_2024
# 7. Aporte del Gobierno Central: P041_2019_2022_2024
# 8. Aporte del Gobierno Regional (GORE): P042_2019_2022_2024
# 9. Aporte de las Municipalidades: P043_2019_2022_2024

requested_vars = [
    'P001_2019_2022_2024',
    'P003_2019_2022_2024',
    'P004_2019_2022_2024',
    'P038_2019_2022_2024',
    'P073_2019_2022_2024',
    'P074_2019_2022_2024',
    'P041_2019_2022_2024',
    'P042_2019_2022_2024',
    'P043_2019_2022_2024'
]

print("=== VALUE LABELS FOR REQUESTED VARIABLES ===")
for var in requested_vars:
    print(f"\n--- {var} ---")
    lbls = meta.variable_value_labels.get(var, {})
    print("Labels:", lbls)
    # Check top values across dataset
    counts = df[var].value_counts().head(10)
    print("Counts:", counts.to_dict())

