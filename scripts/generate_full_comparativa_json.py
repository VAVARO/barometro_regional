import sys
sys.stdout.reconfigure(encoding='utf-8')

import pyreadstat
import pandas as pd
import numpy as np
import json

df, meta = pyreadstat.read_sav(r"C:\AGY\BAROMETRO\base_integrada_spss.sav")

# Region definition
regions_list = [
    {"id": 1.0, "region": "O'Higgins", "n": 601, "error": "4.0%", "is_target": False},
    {"id": 2.0, "region": "Ñuble", "n": 500, "error": "4.4%", "is_target": False},
    {"id": 3.0, "region": "Biobío", "n": 500, "error": "4.4%", "is_target": False},
    {"id": 4.0, "region": "Los Ríos", "n": 482, "error": "3.8%", "is_target": False},
    {"id": 5.0, "region": "Los Lagos", "n": 601, "error": "4.0%", "is_target": False},
    {"id": 6.0, "region": "Aysén", "n": 465, "error": "4.5%", "is_target": True},
    {"id": 7.0, "region": "Magallanes", "n": 664, "error": "4.4%", "is_target": False}
]

# Helper for single percentage benchmark (ordered ascending/descending)
def calc_ranked_pct(col, target_vals, order_asc=True):
    if not isinstance(target_vals, list):
        target_vals = [target_vals]
    res = []
    for r in regions_list:
        sub = df[df['region_ord'] == r['id']].copy()
        s_num = pd.to_numeric(sub[col], errors='coerce')
        valid = sub[s_num.notnull() & (s_num < 90)].copy()
        valid['num'] = pd.to_numeric(valid[col], errors='coerce')
        valid['w'] = pd.to_numeric(valid['PonderadorRegional_2019_2022_2024'], errors='coerce').fillna(1.0)
        
        w_tot = valid['w'].sum()
        w_target = valid[valid['num'].isin(target_vals)]['w'].sum()
        pct = round(float(w_target / w_tot * 100), 1) if w_tot > 0 else 0
        
        item = {"region": r['region'], "pct": pct}
        if r['is_target']:
            item["is_target"] = True
        res.append(item)
    return sorted(res, key=lambda x: x['pct'], reverse=not order_asc)

# Helper for 1-7 grade benchmark
def calc_ranked_grade(col):
    res = []
    for r in regions_list:
        sub = df[df['region_ord'] == r['id']].copy()
        s_num = pd.to_numeric(sub[col], errors='coerce')
        valid = sub[s_num.between(1, 7)].copy()
        valid['num'] = pd.to_numeric(valid[col], errors='coerce')
        valid['w'] = pd.to_numeric(valid['PonderadorRegional_2019_2022_2024'], errors='coerce').fillna(1.0)
        
        if len(valid) > 0 and valid['w'].sum() > 0:
            nota = round(float(np.average(valid['num'], weights=valid['w'])), 1)
        else:
            nota = 0.0
            
        item = {"region": r['region'], "nota": nota}
        if r['is_target']:
            item["is_target"] = True
        res.append(item)
    return sorted(res, key=lambda x: x['nota'])

# Helper for stacked categorical distribution per region
def calc_stacked_distribution(col, categories_map):
    # Returns an array of objects per region for Chart.js stacked datasets
    result = []
    for r in regions_list:
        sub = df[df['region_ord'] == r['id']].copy()
        s_num = pd.to_numeric(sub[col], errors='coerce')
        valid = sub[s_num.notnull() & (s_num < 90)].copy()
        valid['num'] = pd.to_numeric(valid[col], errors='coerce')
        valid['w'] = pd.to_numeric(valid['PonderadorRegional_2019_2022_2024'], errors='coerce').fillna(1.0)
        
        w_tot = valid['w'].sum()
        reg_obj = {"region": r['region'], "is_target": r['is_target']}
        
        total_pct = 0
        for code, cat_name in categories_map.items():
            w_cat = valid[valid['num'] == code]['w'].sum()
            pct = round(float(w_cat / w_tot * 100), 1) if w_tot > 0 else 0
            reg_obj[cat_name] = pct
            total_pct += pct
        
        result.append(reg_obj)
    return result

# Helper for text columns like P004
def calc_text_distribution(col, top_n=5):
    result = []
    top_cats = df[col].value_counts().head(top_n).index.tolist()
    for r in regions_list:
        sub = df[df['region_ord'] == r['id']].copy()
        valid = sub[sub[col].notnull()].copy()
        valid['w'] = pd.to_numeric(valid['PonderadorRegional_2019_2022_2024'], errors='coerce').fillna(1.0)
        w_tot = valid['w'].sum()
        
        reg_obj = {"region": r['region'], "is_target": r['is_target']}
        sum_top = 0
        for cat in top_cats:
            w_cat = valid[valid[col] == cat]['w'].sum()
            pct = round(float(w_cat / w_tot * 100), 1) if w_tot > 0 else 0
            reg_obj[cat] = pct
            sum_top += pct
        reg_obj["Otros"] = round(max(0, 100.0 - sum_top), 1)
        result.append(reg_obj)
    return result

# Construct Complete Comparativa JSON
comparativa_data = {
    "ficha_tecnica": [
        { "region": r['region'], "n": r['n'], "error": r['error'], "is_target": r['is_target'] }
        for r in regions_list
    ],
    
    # Preexisting charts
    "estancamiento": calc_ranked_pct('P003_2019_2022_2024', 2.0),
    "confianza": calc_ranked_pct('P020_2019_2022_2024', 1.0),
    "centralismo": [ # G2 asked in Aysén and standard comparison in previous version
        { "region": "Ñuble", "pct": 31 },
        { "region": "O'Higgins", "pct": 37 },
        { "region": "Biobío", "pct": 39 },
        { "region": "Los Ríos", "pct": 44 },
        { "region": "Aysén", "pct": 57, "is_target": True }
    ],
    "seguridad_nota": calc_ranked_grade('P013_2019_2022_2024'),
    "radios_locales": calc_ranked_pct('P037_2024', 4.0),
    "migrar": calc_ranked_pct('P002_2019_2022_2024', 1.0),
    
    # 9 New Charts Requested:
    # 1. Pertenencia Territorial
    "pertenencia_territorial": calc_stacked_distribution('P001_2019_2022_2024', {
        1.0: "Barrio",
        2.0: "Pueblo / Localidad",
        3.0: "Comuna",
        4.0: "Ciudad",
        5.0: "Región",
        6.0: "País"
    }),
    
    # 2. Rumbo Regional Completo
    "rumbo_regional": calc_stacked_distribution('P003_2019_2022_2024', {
        1.0: "Progresando",
        2.0: "Estancada",
        3.0: "En decadencia"
    }),
    
    # 3. Principal Problema de la Región
    "principal_problema": calc_text_distribution('P004_2019_2022_2024', top_n=5),
    
    # 4. Principal Fortaleza Percibida
    "principal_fortaleza": calc_stacked_distribution('P038_2019_2022_2024', {
        4.0: "Riquezas naturales",
        2.0: "Capacidad de trabajo de la gente",
        1.0: "Empresarios y desarrollo",
        8.0: "Calidad de profesionales",
        7.0: "Tradiciones culturales",
        5.0: "Orden y seguridad",
        3.0: "Calidad de autoridades"
    }),
    
    # 5. Apoyo a la Democracia
    "apoyo_democracia": calc_stacked_distribution('P073_2019_2022_2024', {
        1.0: "Democracia preferible",
        2.0: "Gobierno autoritario a veces",
        3.0: "Da lo mismo un régimen u otro",
        4.0: "No sabe / No responde"
    }),
    
    # 6. Autoidentificación Política
    "posicion_politica": calc_stacked_distribution('P074_2019_2022_2024', {
        1.0: "Izquierda",
        2.0: "Centro Izquierda",
        3.0: "Centro",
        4.0: "Centro Derecha",
        5.0: "Derecha",
        6.0: "Ninguna / Independiente"
    }),
    
    # 7. Aporte del Gobierno Central
    "aporte_gob_central": calc_ranked_pct('P041_2019_2022_2024', 1.0),
    
    # 8. Aporte del Gobierno Regional (GORE)
    "aporte_gore": calc_ranked_pct('P042_2019_2022_2024', 1.0),
    
    # 9. Aporte de las Municipalidades
    "aporte_municipios": calc_ranked_pct('P043_2019_2022_2024', 1.0)
}

output_path = r"C:\AGY\BAROMETRO\data\comparativa_interregional.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(comparativa_data, f, ensure_ascii=False, indent=2)

print(f"Updated {output_path} successfully with {len(comparativa_data)} sections!")
