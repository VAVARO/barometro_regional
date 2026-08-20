import pandas as pd
import numpy as np
import json
import os
import pyreadstat

# Load dataset with apply_value_formats=False for clean numerical codes
file_path = "base_integrada_spss.sav" if os.path.exists("base_integrada_spss.sav") else "base_integrada_excel.xlsx"
print(f"Loading {file_path} with apply_value_formats=False...")

if file_path.endswith(".sav"):
    df, meta = pyreadstat.read_sav(file_path, apply_value_formats=False)
else:
    df = pd.read_excel(file_path)

weight_col = "PonderadorRegional_2019_2022_2024" if "PonderadorRegional_2019_2022_2024" in df.columns else [c for c in df.columns if "ponderador" in c.lower()][0]

ord_mapping = {
    1.0: "O'Higgins",
    2.0: "Ñuble",
    3.0: "Biobío",
    4.0: "Los Ríos",
    5.0: "Los Lagos",
    6.0: "Aysén",
    7.0: "Magallanes"
}

df['Region_Clean'] = df['region_ord'].map(ord_mapping)
target_region = "Aysén"

def find_col(target):
    if target in df.columns:
        return target
    for c in df.columns:
        if c.lower() == target.lower():
            return c
    return None

# Helper for weighted mean (Grades 1-7)
def calc_weighted_mean(col_name):
    actual_col = find_col(col_name)
    if not actual_col:
        print(f"WARNING: column {col_name} not found!")
        return []
    res = []
    for reg in ["O'Higgins", "Ñuble", "Biobío", "Los Ríos", "Los Lagos", "Aysén", "Magallanes"]:
        grp = df[df['Region_Clean'] == reg]
        if len(grp) == 0: continue
        s_num = pd.to_numeric(grp[actual_col], errors='coerce')
        valid = grp[s_num.between(1, 7)].copy()
        valid['num'] = pd.to_numeric(valid[actual_col], errors='coerce')
        valid['w'] = pd.to_numeric(valid[weight_col], errors='coerce').fillna(1.0)
        if len(valid) > 0 and valid['w'].sum() > 0:
            w_mean = np.average(valid['num'], weights=valid['w'])
            res.append({"region": reg, "nota": round(float(w_mean), 2), "is_target": (reg == target_region)})
    return sorted(res, key=lambda x: x['nota'], reverse=True)

# Helper for weighted percentage of specific category
def calc_weighted_pct(col_name, target_values):
    actual_col = find_col(col_name)
    if not actual_col:
        print(f"WARNING: column {col_name} not found!")
        return []
    res = []
    if not isinstance(target_values, list):
        target_values = [target_values]
    target_floats = [float(v) for v in target_values if isinstance(v, (int, float, str)) and str(v).replace('.','',1).isdigit()]
    
    for reg in ["O'Higgins", "Ñuble", "Biobío", "Los Ríos", "Los Lagos", "Aysén", "Magallanes"]:
        grp = df[df['Region_Clean'] == reg]
        if len(grp) == 0: continue
        s_num = pd.to_numeric(grp[actual_col], errors='coerce')
        valid = grp[s_num.notna() & (s_num < 90)].copy()
        valid['num'] = pd.to_numeric(valid[actual_col], errors='coerce')
        valid['w'] = pd.to_numeric(valid[weight_col], errors='coerce').fillna(1.0)
        total_w = valid['w'].sum()
        if total_w > 0:
            match_w = valid[valid['num'].isin(target_floats)]['w'].sum()
            pct = round(float((match_w / total_w) * 100), 1)
            res.append({"region": reg, "pct": pct, "is_target": (reg == target_region)})
    return sorted(res, key=lambda x: x['pct'], reverse=True)

# Helper for full category distribution per region (supports both numeric codes and string labels)
def calc_distribution(col_name, val_map):
    actual_col = find_col(col_name)
    if not actual_col:
        print(f"WARNING: column {col_name} not found!")
        return []
    res = []
    
    # Check if keys in val_map are numeric or string
    is_numeric = all(isinstance(k, (int, float)) or (isinstance(k, str) and k.replace('.','',1).isdigit()) for k in val_map.keys())
    
    for reg in ["O'Higgins", "Ñuble", "Biobío", "Los Ríos", "Los Lagos", "Aysén", "Magallanes"]:
        grp = df[df['Region_Clean'] == reg].copy()
        if len(grp) == 0: continue
        
        grp['w'] = pd.to_numeric(grp[weight_col], errors='coerce').fillna(1.0)
        item = {"region": reg, "is_target": (reg == target_region)}
        
        if is_numeric:
            float_map = {float(k): label for k, label in val_map.items()}
            s_num = pd.to_numeric(grp[actual_col], errors='coerce')
            valid = grp[s_num.isin(float_map.keys())].copy()
            valid['num'] = pd.to_numeric(valid[actual_col], errors='coerce')
            total_w = valid['w'].sum()
            if total_w > 0:
                for k_float, label in float_map.items():
                    match_w = valid[valid['num'] == k_float]['w'].sum()
                    item[label] = round(float((match_w / total_w) * 100), 1)
            else:
                for label in float_map.values():
                    item[label] = 0.0
        else:
            # String matching (e.g. 'Seguridad', 'Salud', etc.)
            grp['clean_str'] = grp[actual_col].astype(str).str.strip().str.lower()
            str_map = {str(k).strip().lower(): label for k, label in val_map.items()}
            valid = grp[grp['clean_str'].isin(str_map.keys())].copy()
            total_w = valid['w'].sum()
            if total_w > 0:
                for k_str, label in str_map.items():
                    match_w = valid[valid['clean_str'] == k_str]['w'].sum()
                    item[label] = round(float((match_w / total_w) * 100), 1)
            else:
                for label in str_map.values():
                    item[label] = 0.0
                    
        res.append(item)
    return res

# Compile full JSON structure covering the complete catalog
output_data = {
    "ficha_tecnica": [
        { "region": "O'Higgins", "n": 601, "error": "4.0%" },
        { "region": "Ñuble", "n": 500, "error": "4.4%" },
        { "region": "Biobío", "n": 500, "error": "4.4%" },
        { "region": "Los Ríos", "n": 482, "error": "3.8%" },
        { "region": "Los Lagos", "n": 601, "error": "4.0%" },
        { "region": "Aysén", "n": 465, "error": "4.5%", "is_target": True },
        { "region": "Magallanes", "n": 664, "error": "4.4%" }
    ],
    "coyuntura": {
        "rumbo": calc_distribution("P003_2019_2022_2024", {1: "progresando", 2: "estancada", 3: "decadencia"}),
        "disposicion_migrar": calc_weighted_pct("P002_2019_2022_2024", 1),
        "destino_migracion": calc_distribution("P003_2024", {1: "otra_comuna", 2: "otra_region", 3: "extranjero"}),
        "identificacion_territorial": calc_distribution("P001_2019_2022_2024", {1: "barrio", 3: "comuna", 5: "su_region", 6: "pais"}),
        "principal_problema": calc_distribution("P004_2019_2022_2024", {
            "seguridad": "seguridad",
            "salud": "salud",
            "empleo": "empleo",
            "infraestructura y movilidad": "conectividad",
            "vivienda y urbanismo": "vivienda"
        }),
        "conocimiento_erd": calc_weighted_pct("P040_2024", 1)
    },
    "servicios": {
        "caminos": calc_weighted_mean("P015_2019_2022_2024"),
        "seguridad": calc_weighted_mean("P013_2019_2022_2024"),
        "salud": calc_weighted_mean("P016_2019_2022_2024"),
        "internet": calc_weighted_mean("P019_2019_2022_2024"),
        "vivienda": calc_weighted_mean("P018_2019_2022_2024"),
        "transporte": calc_weighted_mean("P017_2019_2022_2024"),
        "educacion": calc_weighted_mean("P010_2019_2022_2024"),
        "agua": calc_weighted_mean("P008_2019_2022_2024"),
        "medioambiente": calc_weighted_mean("P014_2019_2022_2024"),
        "empleo": calc_weighted_mean("P009_2019_2022_2024"),
        "sueldos": calc_weighted_mean("P011_2019_2022_2024"),
        "recreacion": calc_weighted_mean("P008_2019_2022_2024")
    },
    "descentralizacion": {
        "centralismo": [
            { "region": "Aysén", "pct": 57.0, "is_target": True },
            { "region": "Los Ríos", "pct": 44.0 },
            { "region": "Biobío", "pct": 39.0 },
            { "region": "O'Higgins", "pct": 37.0 },
            { "region": "Ñuble", "pct": 31.0 }
        ],
        "gobernadores": calc_distribution("P059_2019_2022_2024", {1: "impulso", 2: "igual", 3: "problemas"}),
        "decision_obras": calc_weighted_pct("P054_2019_2022_2024", [2, 3]),
        "decision_salud": calc_weighted_pct("P049_2019_2022_2024", [2, 3]),
        "decision_educacion": calc_weighted_pct("P050_2019_2022_2024", [2, 3]),
        "decision_fomento": calc_weighted_pct("P057_2019_2022_2024", [2, 3]),
        "decision_medioambiente": calc_weighted_pct("P053_2019_2022_2024", [2, 3]),
        "decision_agua": calc_weighted_pct("P051_2019_2022_2024", [2, 3]),
        "decision_vivienda": calc_weighted_pct("P052_2019_2022_2024", [2, 3]),
        "decision_inversion": calc_weighted_pct("P055_2019_2022_2024", [2, 3]),
        "decision_seguridad": calc_weighted_pct("P056_2019_2022_2024", [2, 3]),
        "aporte_institucional": [
            {"institucion": "Universidades Regionales", "pct": 65.0},
            {"institucion": "Medios Regionales", "pct": 63.0},
            {"institucion": "Municipalidades", "pct": 55.0},
            {"institucion": "Organizaciones Sociales", "pct": 51.0},
            {"institucion": "Gobierno Regional (GORE)", "pct": 49.0},
            {"institucion": "Empresas Regionales", "pct": 49.0},
            {"institucion": "Gobierno Central", "pct": 37.0},
            {"institucion": "Parlamentarios", "pct": 24.0}
        ]
    },
    "cohesion": {
        "confianza": calc_weighted_pct("P020_2019_2022_2024", 1),
        "participacion_comunitaria": calc_weighted_pct("P021_2019_2022_2024", 1),
        "afectacion_aire": calc_weighted_pct("P024_2019_2022_2024", 1),
        "afectacion_extractivismo": calc_weighted_pct("P026_2019_2022_2024", 1),
        "afectacion_basura": calc_weighted_pct("P025_2019_2022_2024", 1),
        "afectacion_agua": calc_weighted_pct("P023_2019_2022_2024", 1),
        "afectacion_clima": calc_weighted_pct("P029_2019_2022_2024", 1),
        "adhesion_democracia": calc_weighted_pct("P073_2019_2022_2024", 1),
        "uso_radios": calc_weighted_pct("P033_2024", 1),
        "uso_tv": calc_weighted_pct("P030_2024", 1),
        "medio_principal": calc_distribution("P037_2024", {1: "redes_sociales", 2: "tv_abierta", 4: "radios_locales", 5: "prensa_digital"})
    }
}

os.makedirs("data", exist_ok=True)
with open("data/comparativa_interregional.json", "w", encoding="utf-8") as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print("Successfully generated data/comparativa_interregional.json!")
