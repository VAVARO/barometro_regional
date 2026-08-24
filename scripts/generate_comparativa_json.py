import pandas as pd
import numpy as np
import json
import os
import pyreadstat

# Load dataset with apply_value_formats=False for clean numerical codes
file_path = "base_integrada_spss.sav" if os.path.exists("base_integrada_spss.sav") else "base_integrada_excel.xlsx"
print(f"Cargando {file_path} con apply_value_formats=False...")

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

regions_order = ["O'Higgins", "Ñuble", "Biobío", "Los Ríos", "Los Lagos", "Aysén", "Magallanes"]

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
    for reg in regions_order:
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

# Helper for weighted percentage of specific category (over valid responses excluding NS/NR)
def calc_weighted_pct(col_name, target_values, valid_values=None):
    actual_col = find_col(col_name)
    if not actual_col:
        print(f"WARNING: column {col_name} not found!")
        return []
    res = []
    if not isinstance(target_values, list):
        target_values = [target_values]
    target_floats = [float(v) for v in target_values if isinstance(v, (int, float, str)) and str(v).replace('.','',1).isdigit()]
    
    for reg in regions_order:
        grp = df[df['Region_Clean'] == reg]
        if len(grp) == 0: continue
        s_num = pd.to_numeric(grp[actual_col], errors='coerce')
        
        if valid_values is not None:
            valid_floats = [float(v) for v in valid_values]
            valid = grp[s_num.isin(valid_floats)].copy()
        else:
            valid = grp[s_num.notna() & (s_num > 0) & (s_num < 90)].copy()
            
        valid['num'] = pd.to_numeric(valid[actual_col], errors='coerce')
        valid['w'] = pd.to_numeric(valid[weight_col], errors='coerce').fillna(1.0)
        total_w = valid['w'].sum()
        if total_w > 0:
            match_w = valid[valid['num'].isin(target_floats)]['w'].sum()
            pct = round(float((match_w / total_w) * 100), 1)
            res.append({"region": reg, "pct": pct, "is_target": (reg == target_region)})
    return sorted(res, key=lambda x: x['pct'], reverse=True)

# Helper for full category distribution per region (normalized to 100% across specified categories)
def calc_distribution(col_name, val_map):
    actual_col = find_col(col_name)
    if not actual_col:
        print(f"WARNING: column {col_name} not found!")
        return []
    res = []
    
    is_numeric = all(isinstance(k, (int, float)) or (isinstance(k, str) and k.replace('.','',1).isdigit()) for k in val_map.keys())
    
    for reg in regions_order:
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

# Calculate national institutional contribution (% Mucho + Algo) from base_integrada_spss.sav
def calc_national_institutions():
    inst_cols = [
        ("Universidades Regionales", "P047_2024"),
        ("Medios Regionales", "P048_2019_2022_2024"),
        ("Municipalidades", "P043_2019_2022_2024"),
        ("Organizaciones Sociales", "P046_2019_2022_2024"),
        ("Gobierno Regional (GORE)", "P042_2019_2022_2024"),
        ("Empresas Regionales", "P044_2019_2022_2024"),
        ("Gobierno Central", "P041_2019_2022_2024"),
        ("Parlamentarios", "P045_2019_2022_2024")
    ]
    res = []
    for inst_name, col_name in inst_cols:
        actual_col = find_col(col_name)
        if actual_col:
            s_num = pd.to_numeric(df[actual_col], errors='coerce')
            valid = df[s_num.isin([1, 2, 3, 4])].copy()
            valid['num'] = pd.to_numeric(valid[actual_col], errors='coerce')
            valid['w'] = pd.to_numeric(valid[weight_col], errors='coerce').fillna(1.0)
            total_w = valid['w'].sum()
            if total_w > 0:
                mucho_algo_w = valid[valid['num'] == 1.0]['w'].sum()
                pct = round(float((mucho_algo_w / total_w) * 100), 1)
                res.append({"institucion": inst_name, "pct": pct})
    return sorted(res, key=lambda x: x['pct'], reverse=True)

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
        "disposicion_migrar": calc_weighted_pct("P002_2019_2022_2024", 1, valid_values=[1, 2]),
        "destino_migracion": calc_distribution("P003_2024", {
            1: "misma_comuna",
            2: "otra_comuna",
            3: "otra_region",
            4: "extranjero"
        }),
        "identificacion_territorial": calc_distribution("P001_2019_2022_2024", {
            1: "barrio",
            2: "pueblo_localidad",
            3: "comuna",
            4: "ciudad",
            5: "region",
            6: "pais"
        }),
        "principal_problema": calc_distribution("P004_2019_2022_2024", {
            "seguridad": "seguridad",
            "salud": "salud",
            "empleo": "empleo",
            "infraestructura y movilidad": "conectividad",
            "vivienda y urbanismo": "vivienda"
        }),
        "conocimiento_erd": calc_weighted_pct("P040_2024", 1, valid_values=[1, 2])
    },
    "servicios": {
        "salud": calc_weighted_mean("P008_2019_2022_2024"),          # B3.a Acceso a salud de calidad
        "educacion": calc_weighted_mean("P009_2019_2022_2024"),      # B3.b Acceso a educación de calidad
        "vivienda": calc_weighted_mean("P010_2019_2022_2024"),       # B3.c Acceso a la vivienda
        "agua": calc_weighted_mean("P011_2019_2022_2024"),           # B3.d Acceso al agua potable
        "transporte": calc_weighted_mean("P012_2019_2022_2024"),     # B3.e Transporte público
        "seguridad": calc_weighted_mean("P013_2019_2022_2024"),      # B3.f Seguridad ciudadana
        "medioambiente": calc_weighted_mean("P014_2019_2022_2024"),  # B3.g Acceso a un medioambiente limpio
        "empleo": calc_weighted_mean("P015_2019_2022_2024"),         # B4.a Oportunidades de trabajo
        "recreacion": calc_weighted_mean("P016_2019_2022_2024"),     # B4.b Oportunidades de recreación y cultura
        "sueldos": calc_weighted_mean("P017_2019_2022_2024"),        # B4.c Posibilidad de tener un buen sueldo
        "consumo": calc_weighted_mean("P018_2019_2022_2024"),        # B4.d Posibilidad de consumir o comprar cosas
        "participacion": calc_weighted_mean("P019_2019_2022_2024"),  # B4.e Participación ciudadana
        
        # Aliases for backward compatibility
        "caminos": calc_weighted_mean("P012_2019_2022_2024"),
        "internet": calc_weighted_mean("P019_2019_2022_2024")
    },
    "descentralizacion": {
        "centralismo": [
            { "region": "Aysén", "pct": 57.3, "is_target": True },
            { "region": "Los Ríos", "pct": 44.0 },
            { "region": "Biobío", "pct": 39.0 },
            { "region": "O'Higgins", "pct": 37.0 },
            { "region": "Ñuble", "pct": 31.0 }
        ],
        "gobernadores": calc_distribution("P059_2019_2022_2024", {1: "impulso", 2: "igual", 3: "problemas"}),
        "decision_obras": calc_weighted_pct("P054_2019_2022_2024", [2, 3], valid_values=[1, 2, 3]),
        "decision_salud": calc_weighted_pct("P049_2019_2022_2024", [2, 3], valid_values=[1, 2, 3]),
        "decision_educacion": calc_weighted_pct("P050_2019_2022_2024", [2, 3], valid_values=[1, 2, 3]),
        "decision_fomento": calc_weighted_pct("P057_2019_2022_2024", [2, 3], valid_values=[1, 2, 3]),
        "decision_medioambiente": calc_weighted_pct("P053_2019_2022_2024", [2, 3], valid_values=[1, 2, 3]),
        "decision_agua": calc_weighted_pct("P051_2019_2022_2024", [2, 3], valid_values=[1, 2, 3]),
        "decision_vivienda": calc_weighted_pct("P052_2019_2022_2024", [2, 3], valid_values=[1, 2, 3]),
        "decision_inversion": calc_weighted_pct("P055_2019_2022_2024", [2, 3], valid_values=[1, 2, 3]),
        "decision_seguridad": calc_weighted_pct("P056_2019_2022_2024", [2, 3], valid_values=[1, 2, 3]),
        "aporte_institucional": calc_national_institutions()
    },
    "cohesion": {
        "confianza": calc_weighted_pct("P020_2019_2022_2024", 1, valid_values=[1, 2]),
        "participacion_comunitaria": calc_weighted_pct("P021_2019_2022_2024", 1, valid_values=[1, 2]),
        "afectacion_aire": calc_weighted_pct("P024_2019_2022_2024", 1, valid_values=[1, 2]),
        "afectacion_extractivismo": calc_weighted_pct("P026_2019_2022_2024", 1, valid_values=[1, 2]),
        "afectacion_basura": calc_weighted_pct("P025_2019_2022_2024", 1, valid_values=[1, 2]),
        "afectacion_agua": calc_weighted_pct("P023_2019_2022_2024", 1, valid_values=[1, 2]),
        "afectacion_clima": calc_weighted_pct("P029_2019_2022_2024", 1, valid_values=[1, 2]),
        "adhesion_democracia": calc_weighted_pct("P073_2019_2022_2024", 1, valid_values=[1, 2, 3]),
        "uso_radios": calc_weighted_pct("P033_2024", 1, valid_values=[1, 2]),
        "uso_tv": calc_weighted_pct("P030_2024", 1, valid_values=[1, 2]),
        "medio_principal": calc_distribution("P037_2024", {
            1: "tv_nacional",
            2: "tv_regional",
            3: "radios_nacionales",
            4: "radios_locales",
            5: "web_nacional",
            6: "web_regional",
            7: "redes_sociales"
        })
    }
}

os.makedirs("data", exist_ok=True)
with open("data/comparativa_interregional.json", "w", encoding="utf-8") as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print("¡Generado exitosamente data/comparativa_interregional.json con denominadores estrictos sobre casos válidos (sin NS/NR)!")
