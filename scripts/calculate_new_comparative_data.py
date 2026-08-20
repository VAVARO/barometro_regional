import sys
sys.stdout.reconfigure(encoding='utf-8')

import pyreadstat
import pandas as pd
import numpy as np
import json

df, meta = pyreadstat.read_sav(r"C:\AGY\BAROMETRO\base_integrada_spss.sav")

regions = [
    {"id": 1.0, "name": "O'Higgins", "is_target": False},
    {"id": 2.0, "name": "Ñuble", "is_target": False},
    {"id": 3.0, "name": "Biobío", "is_target": False},
    {"id": 4.0, "name": "Los Ríos", "is_target": False},
    {"id": 5.0, "name": "Los Lagos", "is_target": False},
    {"id": 6.0, "name": "Aysén", "is_target": True},
    {"id": 7.0, "name": "Magallanes", "is_target": False}
]

# Function to get weighted percentage for a single target value
def get_weighted_pct(col, target_val):
    result = []
    for r in regions:
        sub = df[df['region_ord'] == r['id']].copy()
        s_num = pd.to_numeric(sub[col], errors='coerce')
        valid = sub[s_num.notnull() & (s_num < 90)].copy()
        valid['num'] = pd.to_numeric(valid[col], errors='coerce')
        valid['w'] = pd.to_numeric(valid['PonderadorRegional_2019_2022_2024'], errors='coerce').fillna(1.0)
        
        w_total = valid['w'].sum()
        w_target = valid[valid['num'] == target_val]['w'].sum()
        pct = round(float(w_target / w_total * 100), 1) if w_total > 0 else 0
        
        item = {"region": r['name'], "pct": pct}
        if r['is_target']:
            item["is_target"] = True
        result.append(item)
    # sort by pct ascending or descending
    return sorted(result, key=lambda x: x['pct'])

# Function for stacked / categorical distribution
def get_category_dist(col, val_labels_map):
    result = {}
    for r in regions:
        sub = df[df['region_ord'] == r['id']].copy()
        s_num = pd.to_numeric(sub[col], errors='coerce')
        valid = sub[s_num.notnull() & (s_num < 90)].copy()
        valid['num'] = pd.to_numeric(valid[col], errors='coerce')
        valid['w'] = pd.to_numeric(valid['PonderadorRegional_2019_2022_2024'], errors='coerce').fillna(1.0)
        
        w_total = valid['w'].sum()
        dist = {}
        for code, label in val_labels_map.items():
            w_cat = valid[valid['num'] == code]['w'].sum()
            dist[label] = round(float(w_cat / w_total * 100), 1) if w_total > 0 else 0
        result[r['name']] = dist
    return result

# String column categories (like P004)
def get_string_category_dist(col):
    result = {}
    # Top categories overall
    top_cats = df[col].value_counts().head(6).index.tolist()
    for r in regions:
        sub = df[df['region_ord'] == r['id']].copy()
        valid = sub[sub[col].notnull()].copy()
        valid['w'] = pd.to_numeric(valid['PonderadorRegional_2019_2022_2024'], errors='coerce').fillna(1.0)
        w_total = valid['w'].sum()
        dist = {}
        for cat in top_cats:
            w_cat = valid[valid[col] == cat]['w'].sum()
            dist[cat] = round(float(w_cat / w_total * 100), 1) if w_total > 0 else 0
        # remaining is 'Otros'
        known_sum = sum(dist.values())
        dist['Otros'] = round(max(0, 100 - known_sum), 1)
        result[r['name']] = dist
    return result

# Let's test all calculations
comp_payload = {
    # 1. Territorio de Pertenencia
    "pertenencia_territorial": get_category_dist('P001_2019_2022_2024', {
        1.0: "Barrio",
        2.0: "Pueblo/Localidad",
        3.0: "Comuna",
        4.0: "Ciudad",
        5.0: "Región",
        6.0: "País"
    }),
    # 2. Rumbo regional completo
    "rumbo_regional": get_category_dist('P003_2019_2022_2024', {
        1.0: "Progresando",
        2.0: "Estancada",
        3.0: "En decadencia"
    }),
    # 3. Principal problema regional
    "principal_problema": get_string_category_dist('P004_2019_2022_2024'),
    # 4. Principal fortaleza
    "principal_fortaleza": get_category_dist('P038_2019_2022_2024', {
        4.0: "Riquezas naturales",
        2.0: "Capacidad de trabajo de su gente",
        1.0: "Preocupación de empresarios",
        8.0: "Calidad de profesionales",
        7.0: "Tradiciones culturales",
        5.0: "Orden y seguridad",
        3.0: "Calidad de autoridades"
    }),
    # 5. Apoyo a la democracia
    "apoyo_democracia": get_category_dist('P073_2019_2022_2024', {
        1.0: "Democracia preferible",
        2.0: "Autoritarismo a veces",
        3.0: "Da lo mismo",
        4.0: "NS/NR"
    }),
    # 6. Autoidentificación política
    "posicion_politica": get_category_dist('P074_2019_2022_2024', {
        1.0: "Izquierda",
        2.0: "Centro Izquierda",
        3.0: "Centro",
        4.0: "Centro Derecha",
        5.0: "Derecha",
        6.0: "Ninguna / Independiente"
    }),
    # 7. Aporte Gobierno Central (% Mucho + Algo)
    "aporte_gob_central": get_weighted_pct('P041_2019_2022_2024', 1.0),
    # 8. Aporte GORE (% Mucho + Algo)
    "aporte_gore": get_weighted_pct('P042_2019_2022_2024', 1.0),
    # 9. Aporte Municipalidades (% Mucho + Algo)
    "aporte_municipios": get_weighted_pct('P043_2019_2022_2024', 1.0)
}

print("=== SAMPLE OUTPUTS ===")
for k, v in comp_payload.items():
    print(f"\n--- {k} ---")
    if isinstance(v, list):
        print(v[:3])
    else:
        print({rk: rv for rk, rv in list(v.items())[:2]})

with open(r"C:\AGY\BAROMETRO\scripts\new_comparative_data.json", "w", encoding="utf-8") as f:
    json.dump(comp_payload, f, ensure_ascii=False, indent=2)

print("\nSaved new comparative data to scripts/new_comparative_data.json")
