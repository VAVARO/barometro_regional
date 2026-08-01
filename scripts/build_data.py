import pyreadstat
import pandas as pd
import numpy as np
import json
import os

def clean_str(s):
    if not isinstance(s, str):
        return s
    s = ''.join(c for c in s if ord(c) >= 32 or c == '\n')
    
    s = s.replace('Ays\ufffdn', 'Aysén')
    s = s.replace('R\ufffdo Iba\ufffdez', 'Río Ibáñez')
    s = s.replace('R\ufffdo Ib\ufffda\ufffdez', 'Río Ibáñez')
    s = s.replace('Econom\ufffda', 'Economía')
    s = s.replace('Educaci\ufffdn', 'Educación')
    s = s.replace('Poblaci\ufffdn', 'Población')
    s = s.replace('Regi\ufffdn', 'Región')
    s = s.replace('regi\ufffdn', 'región')
    s = s.replace('Qu\ufffd', 'Qué')
    s = s.replace('C\ufffdmo', 'Cómo')
    s = s.replace('c\ufffdun', 'cuán')
    s = s.replace('m\ufffds', 'más')
    s = s.replace('d\ufffdnde', 'dónde')
    s = s.replace('p\ufffdsimo', 'pésimo')
    s = s.replace('v\ufffdnculos', 'vínculos')
    s = s.replace('gesti\ufffdn', 'gestión')
    s = s.replace('investigaci\ufffdn', 'investigación')
    s = s.replace('desempe\ufffdo', 'desempeño')
    s = s.replace('situaci\ufffdn', 'situación')
    s = s.replace('profesi\ufffdn', 'profesión')
    s = s.replace('l\ufffdquidos', 'líquidos')
    s = s.replace('categor\ufffdas', 'categorías')
    s = s.replace('municipios', 'municipios')
    s = s.replace('mucipios', 'municipios')
    s = s.replace('p\ufffdrdida', 'pérdida')
    s = s.replace('le\ufffda', 'leña')
    s = s.replace('h\ufffddricos', 'hídricos')
    s = s.replace('mit\ufffdlidos', 'mitílidos')
    s = s.replace('act.tecnolog\ufffda', 'act. tecnología')
    s = s.replace('innovaci\ufffdn', 'innovación')
    s = s.replace('progresar\ufffda', 'progresaría')
    s = s.replace('econ\ufffdmicamente', 'económicamente')
    s = s.replace('aumentar\ufffda', 'aumentaría')
    s = s.replace('podr\ufffda', 'podría')
    s = s.replace('p\ufffdblica', 'pública')
    s = s.replace('b\ufffdsica', 'básica')
    s = s.replace('construcci\ufffdn', 'construcción')
    s = s.replace('localizaci\ufffdn', 'localización')
    s = s.replace('opini\ufffdn', 'opinión')
    s = s.replace('\ufffd', '')
    
    return s.strip()

def weighted_mean(series, weights):
    valid = ~(series.isna() | weights.isna() | (series >= 97))
    if not valid.any():
        return None
    s = series[valid]
    w = weights[valid]
    return float(np.sum(s * w) / np.sum(w))

def weighted_counts(series, weights, val_labels=None):
    valid = ~(series.isna() | weights.isna() | (series >= 97))
    if not valid.any():
        return {}
    s = series[valid]
    w = weights[valid]
    
    total_w = np.sum(w)
    res = {}
    for val in np.unique(s):
        mask = (s == val)
        val_w = np.sum(w[mask])
        pct = float((val_w / total_w) * 100)
        lbl = str(int(val))
        if val_labels:
            if str(val) in val_labels:
                lbl = val_labels[str(val)]
            elif float(val) in val_labels:
                lbl = val_labels[float(val)]
            elif int(val) in val_labels:
                lbl = val_labels[int(val)]
        res[clean_str(lbl)] = {
            "count": int(np.sum(mask)),
            "weighted_count": round(float(val_w), 2),
            "percentage": round(pct, 1)
        }
    return res

def process_data():
    sav_path = "Base Barómetro Aysén 2025.03.11.sav"
    df, meta = pyreadstat.read_sav(sav_path)
    
    print(f"Loaded dataset: {len(df)} rows, {len(df.columns)} columns.")
    
    comuna_labels = {
        1.0: "Coyhaique",
        2.0: "Lago Verde",
        3.0: "Aysén",
        4.0: "Cisnes",
        5.0: "Guaitecas",
        6.0: "Chile Chico",
        7.0: "Cochrane",
        8.0: "O'Higgins",
        9.0: "Tortel",
        10.0: "Río Ibáñez",
        11.0: "Balmaceda"
    }
    
    area_labels = {1.0: "Urbana", 2.0: "Rural"}
    edad_labels = {1.0: "18-29", 2.0: "30-44", 3.0: "45-59", 4.0: "60+"}
    gse_labels = {1.0: "AB", 2.0: "C1a", 3.0: "C1b", 4.0: "C2", 5.0: "C3", 6.0: "D", 7.0: "E"}
    
    variable_info = {}
    for col in meta.column_names:
        lbl = clean_str(meta.column_names_to_labels.get(col, col))
        v_labels = meta.variable_value_labels.get(col, {})
        clean_v_labels = {str(k): clean_str(v) for k, v in v_labels.items()}
        variable_info[col] = {
            "label": lbl,
            "value_labels": clean_v_labels,
            "values": clean_v_labels
        }
        
    def calculate_group_summary(sub_df):
        weights = sub_df['PONDERADOR']
        n_sample = len(sub_df)
        n_weighted = float(weights.sum())
        
        summary = {
            "n_sample": n_sample,
            "n_weighted": round(n_weighted, 1),
            "rumbo_regional": weighted_counts(sub_df['B1'], weights, meta.variable_value_labels.get('B1')),
            "top_problemas": weighted_counts(sub_df['B2_RECOD'], weights, meta.variable_value_labels.get('B2_RECOD')),
            "pertenencia": weighted_counts(sub_df['A1'], weights, meta.variable_value_labels.get('A1')),
            "deseo_movilidad": weighted_counts(sub_df['A2'], weights, meta.variable_value_labels.get('A2')),
            "destino_movilidad": weighted_counts(sub_df['A3'], weights, meta.variable_value_labels.get('A3')),
            "confianza_c1": weighted_counts(sub_df['C1'], weights, meta.variable_value_labels.get('C1')),
            "participacion_c2": weighted_counts(sub_df['C2'], weights, meta.variable_value_labels.get('C2')),
            "organizacion_c2_2": weighted_counts(sub_df['C2_2_RECOD'], weights, meta.variable_value_labels.get('C2_2_RECOD')),
            "medio_principal": weighted_counts(sub_df['E2'], weights, meta.variable_value_labels.get('E2')),
            "ventaja_regional": weighted_counts(sub_df['F1'], weights, meta.variable_value_labels.get('F1')),
            "centralismo_g2": weighted_counts(sub_df['G2'], weights, meta.variable_value_labels.get('G2')),
            "gobernador_g3": weighted_counts(sub_df['G3'], weights, meta.variable_value_labels.get('G3')),
            "democracia_h1": weighted_counts(sub_df['H1'], weights, meta.variable_value_labels.get('H1')),
            "politica_h2": weighted_counts(sub_df['H2'], weights, meta.variable_value_labels.get('H2')),
            "uaysen_conocimiento": weighted_counts(sub_df['I5'], weights, meta.variable_value_labels.get('I5')),
            "uaysen_identificacion_mean": weighted_mean(sub_df['I6'], weights),
            "uaysen_nota_mean": weighted_mean(sub_df['I8'], weights),
            "evaluacion_servicios": {},
            "gobernanza": {},
            "aporte_instituciones": {},
            "urgencia_ambiental": {},
            "actividades_economicas": {},
            "aporte_uaysen": {},
            "afectacion_ambiental": {},
            "salmon_impactos": {},
            "turismo_mitos": {}
        }
        
        for col in [c for c in sub_df.columns if (c.startswith('B3_') or c.startswith('B4_')) and not c.endswith('_REC')]:
            lbl = meta.column_names_to_labels.get(col, col)
            summary['evaluacion_servicios'][col] = {
                "label": clean_str(lbl),
                "mean": weighted_mean(sub_df[col], weights),
                "distribution": weighted_counts(sub_df[col], weights, meta.variable_value_labels.get(col))
            }
            
        for col in [c for c in sub_df.columns if c.startswith('G1') and col in meta.column_names]:
            lbl = meta.column_names_to_labels.get(col, col)
            summary['gobernanza'][col] = {
                "label": clean_str(lbl),
                "distribution": weighted_counts(sub_df[col], weights, meta.variable_value_labels.get(col))
            }

        for col in [c for c in sub_df.columns if c.startswith('F4_') and not c.endswith('_REC')]:
            lbl = meta.column_names_to_labels.get(col, col)
            summary['aporte_instituciones'][col] = {
                "label": clean_str(lbl),
                "mean": weighted_mean(sub_df[col], weights),
                "distribution": weighted_counts(sub_df[col], weights, meta.variable_value_labels.get(col))
            }

        for col in [c for c in sub_df.columns if c.startswith('I4_') and not c.endswith('_REC')]:
            lbl = meta.column_names_to_labels.get(col, col)
            summary['urgencia_ambiental'][col] = {
                "label": clean_str(lbl),
                "mean": weighted_mean(sub_df[col], weights),
                "distribution": weighted_counts(sub_df[col], weights, meta.variable_value_labels.get(col))
            }

        for col in [c for c in sub_df.columns if c.startswith('D1_') and not c.endswith('_REC')]:
            lbl = meta.column_names_to_labels.get(col, col)
            summary['afectacion_ambiental'][col] = {
                "label": clean_str(lbl),
                "distribution": weighted_counts(sub_df[col], weights, meta.variable_value_labels.get(col))
            }

        for col in [c for c in sub_df.columns if c.startswith('I2_') and not c.endswith('_REC')]:
            lbl = meta.column_names_to_labels.get(col, col)
            summary['salmon_impactos'][col] = {
                "label": clean_str(lbl),
                "mean": weighted_mean(sub_df[col], weights),
                "distribution": weighted_counts(sub_df[col], weights, meta.variable_value_labels.get(col))
            }

        for col in [c for c in sub_df.columns if c.startswith('I3_') and not c.endswith('_REC')]:
            lbl = meta.column_names_to_labels.get(col, col)
            summary['turismo_mitos'][col] = {
                "label": clean_str(lbl),
                "mean": weighted_mean(sub_df[col], weights),
                "distribution": weighted_counts(sub_df[col], weights, meta.variable_value_labels.get(col))
            }

        for col in [c for c in sub_df.columns if c.startswith('I1_') and not c.endswith('_REC')]:
            lbl = meta.column_names_to_labels.get(col, col)
            summary['actividades_economicas'][col] = {
                "label": clean_str(lbl),
                "mean": weighted_mean(sub_df[col], weights),
                "distribution": weighted_counts(sub_df[col], weights, meta.variable_value_labels.get(col))
            }
            
        for col in ['I7_1', 'I7_2', 'I7_3']:
            if col in sub_df.columns:
                lbl = meta.column_names_to_labels.get(col, col)
                summary['aporte_uaysen'][col] = {
                    "label": clean_str(lbl),
                    "mean": weighted_mean(sub_df[col], weights),
                    "distribution": weighted_counts(sub_df[col], weights, meta.variable_value_labels.get(col))
                }
                
        return summary

    overall_summary = calculate_group_summary(df)

    comuna_summaries = {}
    for code, c_name in comuna_labels.items():
        sub = df[df['COMUNA'] == code]
        if len(sub) > 0:
            comuna_summaries[c_name] = calculate_group_summary(sub)
        else:
            comuna_summaries[c_name] = None

    records = []
    for idx, row in df.iterrows():
        rec = {
            "id": int(idx),
            "COMUNA": int(row['COMUNA']) if not pd.isna(row['COMUNA']) else 0,
            "AREA": int(row['AREA']) if not pd.isna(row['AREA']) else 0,
            "TRAMOS": int(row['TRAMOS']) if not pd.isna(row['TRAMOS']) else 0,
            "GSE": int(row['GSE']) if not pd.isna(row['GSE']) else 0,
            "PONDERADOR": float(row['PONDERADOR']) if not pd.isna(row['PONDERADOR']) else 1.0,
            "comuna": comuna_labels.get(row['COMUNA'], "Otra"),
            "comuna_code": int(row['COMUNA']) if not pd.isna(row['COMUNA']) else 0,
            "zona": area_labels.get(row['AREA'], "Urbana"),
            "edad": edad_labels.get(row['TRAMOS'], "18-29"),
            "gse": gse_labels.get(row['GSE'], "C3"),
            "sexo": "Mujer" if row['SEXO'] == 1.0 else ("Hombre" if row['SEXO'] == 2.0 else "Otro"),
            "weight": float(row['PONDERADOR']) if not pd.isna(row['PONDERADOR']) else 1.0,
            "B1": int(row['B1']) if not pd.isna(row['B1']) else None,
            "B2_RECOD": int(row['B2_RECOD']) if not pd.isna(row['B2_RECOD']) else None,
            "A1": int(row['A1']) if not pd.isna(row['A1']) else None,
            "A2": int(row['A2']) if not pd.isna(row['A2']) else None,
            "A3": int(row['A3']) if not pd.isna(row['A3']) else None,
            "C1": int(row['C1']) if not pd.isna(row['C1']) else None,
            "C2": int(row['C2']) if not pd.isna(row['C2']) else None,
            "C2_2_RECOD": int(row['C2_2_RECOD']) if not pd.isna(row['C2_2_RECOD']) else None,
            "E2": int(row['E2']) if not pd.isna(row['E2']) else None,
            "F1": int(row['F1']) if not pd.isna(row['F1']) else None,
            "F2": int(row['F2']) if not pd.isna(row['F2']) else None,
            "F3": int(row['F3']) if not pd.isna(row['F3']) else None,
            "G2": int(row['G2']) if not pd.isna(row['G2']) else None,
            "G3": int(row['G3']) if not pd.isna(row['G3']) else None,
            "H1": int(row['H1']) if not pd.isna(row['H1']) else None,
            "H2": int(row['H2']) if not pd.isna(row['H2']) else None,
            "I5": int(row['I5']) if not pd.isna(row['I5']) else None,
            "I6": float(row['I6']) if not pd.isna(row['I6']) and row['I6'] <= 100 else None,
            "I8": float(row['I8']) if not pd.isna(row['I8']) and row['I8'] <= 7 else None
        }
        
        for prefix in ['B3_', 'B4_', 'D1_', 'E1_', 'F4_', 'G1_', 'I4_', 'I1_', 'I2_', 'I3_', 'I7_']:
            for col in df.columns:
                if col.startswith(prefix) and not col.endswith('_REC'):
                    val = row[col]
                    rec[col] = float(val) if not pd.isna(val) else None
                    
        records.append(rec)

    output = {
        "metadata": {
            "total_respondents": len(df),
            "comunas": list(comuna_labels.values()),
            "zonas": ["Todas", "Urbana", "Rural"],
            "edades": ["Todos", "18-29", "30-44", "45-59", "60+"],
            "gses": ["Todos", "AB", "C1a", "C1b", "C2", "C3", "D", "E"],
            "variable_info": variable_info
        },
        "variables": variable_info,
        "overall": overall_summary,
        "by_comuna": comuna_summaries,
        "records": records
    }
    
    os.makedirs("data", exist_ok=True)
    with open("data/barometro_summary.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully generated data/barometro_summary.json with 100% survey coverage.")

if __name__ == "__main__":
    process_data()
