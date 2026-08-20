import sys
sys.stdout.reconfigure(encoding='utf-8')

import pyreadstat
import pandas as pd
import numpy as np
import json

df, meta = pyreadstat.read_sav(r"C:\AGY\BAROMETRO\base_integrada_spss.sav", encoding="latin1")

# Clean region list with correct UTF-8 names
regions_list = [
    {"id": 1.0, "region": "O'Higgins", "n": 601, "error": "4.0%", "is_target": False},
    {"id": 2.0, "region": "Ñuble", "n": 500, "error": "4.4%", "is_target": False},
    {"id": 3.0, "region": "Biobío", "n": 500, "error": "4.4%", "is_target": False},
    {"id": 4.0, "region": "Los Ríos", "n": 482, "error": "3.8%", "is_target": False},
    {"id": 5.0, "region": "Los Lagos", "n": 601, "error": "4.0%", "is_target": False},
    {"id": 6.0, "region": "Aysén", "n": 465, "error": "4.5%", "is_target": True},
    {"id": 7.0, "region": "Magallanes", "n": 664, "error": "4.4%", "is_target": False}
]

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

def calc_stacked_distribution(col, categories_map):
    result = []
    for r in regions_list:
        sub = df[df['region_ord'] == r['id']].copy()
        s_num = pd.to_numeric(sub[col], errors='coerce')
        valid = sub[s_num.notnull() & (s_num < 90)].copy()
        valid['num'] = pd.to_numeric(valid[col], errors='coerce')
        valid['w'] = pd.to_numeric(valid['PonderadorRegional_2019_2022_2024'], errors='coerce').fillna(1.0)
        
        w_tot = valid['w'].sum()
        reg_obj = {"region": r['region'], "is_target": r['is_target']}
        
        for code, cat_name in categories_map.items():
            w_cat = valid[valid['num'] == code]['w'].sum()
            pct = round(float(w_cat / w_tot * 100), 1) if w_tot > 0 else 0
            reg_obj[cat_name] = pct
        
        result.append(reg_obj)
    return result

# Clean problems distribution (string normalization)
def calc_clean_problem_distribution(col):
    result = []
    category_names = [
        "Seguridad",
        "Infraestructura y movilidad",
        "Salud",
        "Empleo",
        "Economía",
        "Otros"
    ]
    
    for r in regions_list:
        sub = df[df['region_ord'] == r['id']].copy()
        valid = sub[sub[col].notnull()].copy()
        valid['w'] = pd.to_numeric(valid['PonderadorRegional_2019_2022_2024'], errors='coerce').fillna(1.0)
        w_tot = valid['w'].sum()
        
        reg_obj = {"region": r['region'], "is_target": r['is_target']}
        
        # normalize string values
        for cat in ["Seguridad", "Infraestructura y movilidad", "Salud", "Empleo"]:
            w_cat = valid[valid[col].astype(str).str.contains(cat[:6], case=False, na=False)]['w'].sum()
            pct = round(float(w_cat / w_tot * 100), 1) if w_tot > 0 else 0
            reg_obj[cat] = pct
            
        # Economía / Economia
        w_econ = valid[valid[col].astype(str).str.contains("Econom", case=False, na=False)]['w'].sum()
        reg_obj["Economía"] = round(float(w_econ / w_tot * 100), 1) if w_tot > 0 else 0
        
        sum_known = reg_obj["Seguridad"] + reg_obj["Infraestructura y movilidad"] + reg_obj["Salud"] + reg_obj["Empleo"] + reg_obj["Economía"]
        reg_obj["Otros"] = round(max(0, 100.0 - sum_known), 1)
        result.append(reg_obj)
        
    return result

comparativa_data = {
    "ficha_tecnica": [
        { "region": r['region'], "n": r['n'], "error": r['error'], "is_target": r['is_target'] }
        for r in regions_list
    ],
    
    "estancamiento": calc_ranked_pct('P003_2019_2022_2024', 2.0),
    "confianza": calc_ranked_pct('P020_2019_2022_2024', 1.0),
    "centralismo": [
        { "region": "Ñuble", "pct": 31.0 },
        { "region": "O'Higgins", "pct": 37.0 },
        { "region": "Biobío", "pct": 39.0 },
        { "region": "Los Ríos", "pct": 44.0 },
        { "region": "Aysén", "pct": 57.0, "is_target": True }
    ],
    "seguridad_nota": calc_ranked_grade('P013_2019_2022_2024'),
    "radios_locales": calc_ranked_pct('P037_2024', 4.0),
    "migrar": calc_ranked_pct('P002_2019_2022_2024', 1.0),
    
    "pertenencia_territorial": calc_stacked_distribution('P001_2019_2022_2024', {
        1.0: "Barrio",
        2.0: "Pueblo / Localidad",
        3.0: "Comuna",
        4.0: "Ciudad",
        5.0: "Región",
        6.0: "País"
    }),
    
    "rumbo_regional": calc_stacked_distribution('P003_2019_2022_2024', {
        1.0: "Progresando",
        2.0: "Estancada",
        3.0: "En decadencia"
    }),
    
    "principal_problema": calc_clean_problem_distribution('P004_2019_2022_2024'),
    
    "principal_fortaleza": calc_stacked_distribution('P038_2019_2022_2024', {
        4.0: "Riquezas naturales",
        2.0: "Capacidad de trabajo de la gente",
        1.0: "Empresarios y desarrollo",
        8.0: "Calidad de profesionales",
        7.0: "Tradiciones culturales",
        5.0: "Orden y seguridad",
        3.0: "Calidad de autoridades"
    }),
    
    "apoyo_democracia": calc_stacked_distribution('P073_2019_2022_2024', {
        1.0: "Democracia preferible",
        2.0: "Gobierno autoritario a veces",
        3.0: "Da lo mismo un régimen u otro",
        4.0: "No sabe / No responde"
    }),
    
    "posicion_politica": calc_stacked_distribution('P074_2019_2022_2024', {
        1.0: "Izquierda",
        2.0: "Centro Izquierda",
        3.0: "Centro",
        4.0: "Centro Derecha",
        5.0: "Derecha",
        6.0: "Ninguna / Independiente"
    }),
    
    "aporte_gob_central": calc_ranked_pct('P041_2019_2022_2024', 1.0),
    "aporte_gore": calc_ranked_pct('P042_2019_2022_2024', 1.0),
    "aporte_municipios": calc_ranked_pct('P043_2019_2022_2024', 1.0)
}

output_path = r"C:\AGY\BAROMETRO\data\comparativa_interregional.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(comparativa_data, f, ensure_ascii=False, indent=2)

print("Saved clean UTF-8 JSON successfully!")
