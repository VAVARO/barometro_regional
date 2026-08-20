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

def calc_regional_metric(col_name, metric_type='distribution', target_val=None):
    res = {}
    for r_code, r_name in regions.items():
        sub = df[df['region_ord'] == r_code].copy()
        s_num = pd.to_numeric(sub[col_name], errors='coerce')
        valid = sub[s_num.notnull() & (s_num < 90)].copy() # drop 98/99 NS/NR
        if len(valid) == 0:
            res[r_name] = None
            continue
        
        valid['num_val'] = pd.to_numeric(valid[col_name], errors='coerce')
        valid['w'] = pd.to_numeric(valid['PonderadorRegional_2019_2022_2024'], errors='coerce').fillna(1.0)
        
        if metric_type == 'mean':
            v_score = valid[valid['num_val'].between(1, 7)]
            if len(v_score) == 0:
                res[r_name] = None
            else:
                mean_val = np.average(v_score['num_val'], weights=v_score['w'])
                res[r_name] = round(float(mean_val), 2)
        elif metric_type == 'target_pct':
            w_total = valid['w'].sum()
            w_target = valid[valid['num_val'] == target_val]['w'].sum()
            res[r_name] = round(float(w_target / w_total * 100), 1)
        elif metric_type == 'full_dist':
            w_total = valid['w'].sum()
            dist = {}
            for v_cat in sorted(valid['num_val'].unique()):
                w_cat = valid[valid['num_val'] == v_cat]['w'].sum()
                dist[str(v_cat)] = round(float(w_cat / w_total * 100), 1)
            res[r_name] = dist
            
    return res

modules = {
    "Módulo 1: Identidad, Pertenencia y Migración": [
        {"id": "comp_identidad_territorio", "col": "P001_2019_2022_2024", "type": "full_dist", "title": "Sentido de pertenencia territorial prioritario (Barrio vs Comuna vs Región vs País)", "in_app": False},
        {"id": "comp_migrar", "col": "P002_2019_2022_2024", "type": "target_pct", "target": 1.0, "title": "Disposición a migrar / irse de la región (%)", "in_app": True},
        {"id": "comp_destino_migracion", "col": "P003_2024", "type": "full_dist", "title": "Destino preferido de migración (Otra comuna / Otra región / Extranjero)", "in_app": False}
    ],
    "Módulo 2: Evaluación del Rumbo Regional y Problemas": [
        {"id": "comp_estancamiento", "col": "P003_2019_2022_2024", "type": "target_pct", "target": 2.0, "title": "Percepción de estancamiento regional (%)", "in_app": True},
        {"id": "comp_rumbo_completo", "col": "P003_2019_2022_2024", "type": "full_dist", "title": "Rumbo de la región: Progresando vs Estancada vs En Decadencia (%)", "in_app": False},
        {"id": "comp_problemas_1", "col": "P004_2019_2022_2024", "type": "full_dist", "title": "Principal problema percibido en la región (%)", "in_app": False},
        {"id": "comp_problemas_2", "col": "P007_2019_2022_2024", "type": "full_dist", "title": "Segundo problema percibido en la región (%)", "in_app": False}
    ],
    "Módulo 3: Evaluación de Dimensiones de Desarrollo y Calidad de Vida (Notas 1.0 a 7.0)": [
        {"id": "comp_nota_recreacion", "col": "P008_2019_2022_2024", "type": "mean", "title": "Oportunidades de recreación y cultura (Nota 1.0 a 7.0)", "in_app": False},
        {"id": "comp_nota_empleo", "col": "P009_2019_2022_2024", "type": "mean", "title": "Posibilidad de encontrar trabajo (Nota 1.0 a 7.0)", "in_app": False},
        {"id": "comp_nota_educacion", "col": "P010_2019_2022_2024", "type": "mean", "title": "Oportunidades educacionales (Nota 1.0 a 7.0)", "in_app": False},
        {"id": "comp_nota_sueldos", "col": "P011_2019_2022_2024", "type": "mean", "title": "Nivel de remuneraciones y sueldos (Nota 1.0 a 7.0)", "in_app": False},
        {"id": "comp_nota_participacion", "col": "P012_2019_2022_2024", "type": "mean", "title": "Posibilidad de participar en decisiones públicas (Nota 1.0 a 7.0)", "in_app": False},
        {"id": "comp_nota_seguridad", "col": "P013_2019_2022_2024", "type": "mean", "title": "Seguridad ciudadana y combate a la delincuencia (Nota 1.0 a 7.0)", "in_app": True},
        {"id": "comp_nota_medioambiente", "col": "P014_2019_2022_2024", "type": "mean", "title": "Calidad ambiental y cuidado del entorno (Nota 1.0 a 7.0)", "in_app": False}
    ],
    "Módulo 4: Evaluación de Servicios Básicos e Infraestructura (Notas 1.0 a 7.0)": [
        {"id": "comp_nota_caminos", "col": "P015_2019_2022_2024", "type": "mean", "title": "Caminos y conectividad vial (Nota 1.0 a 7.0)", "in_app": False},
        {"id": "comp_nota_salud", "col": "P016_2019_2022_2024", "type": "mean", "title": "Servicios de salud pública (Nota 1.0 a 7.0)", "in_app": False},
        {"id": "comp_nota_transporte", "col": "P017_2019_2022_2024", "type": "mean", "title": "Transporte público regional (Nota 1.0 a 7.0)", "in_app": False},
        {"id": "comp_nota_vivienda", "col": "P018_2019_2022_2024", "type": "mean", "title": "Acceso a la vivienda (Nota 1.0 a 7.0)", "in_app": False},
        {"id": "comp_nota_internet", "col": "P019_2019_2022_2024", "type": "mean", "title": "Cobertura y calidad de internet / telecomunicaciones (Nota 1.0 a 7.0)", "in_app": False}
    ],
    "Módulo 5: Confianza Social y Participación Ciudadana": [
        {"id": "comp_confianza", "col": "P020_2019_2022_2024", "type": "target_pct", "target": 1.0, "title": "Confianza interpersonal ('Se puede confiar en las personas') (%)", "in_app": True},
        {"id": "comp_participacion_org", "col": "P021_2019_2022_2024", "type": "target_pct", "target": 1.0, "title": "Participación activa en organizaciones sociales (%)", "in_app": False},
        {"id": "comp_tipo_organizacion", "col": "P022_2024", "type": "full_dist", "title": "Tipo de organizaciones sociales con mayor membresía (%)", "in_app": False}
    ],
    "Módulo 6: Conflictos Socioambientales y Afectación Ciudadana (% Afectado)": [
        {"id": "comp_amb_agua", "col": "P023_2019_2022_2024", "type": "target_pct", "target": 1.0, "title": "Afectado por Escasez / Contaminación del Agua (%)", "in_app": False},
        {"id": "comp_amb_aire", "col": "P024_2019_2022_2024", "type": "target_pct", "target": 1.0, "title": "Afectado por Contaminación del Aire / Humo de leña (%)", "in_app": False},
        {"id": "comp_amb_basura", "col": "P025_2019_2022_2024", "type": "target_pct", "target": 1.0, "title": "Afectado por Basura y Vertederos / Microbasurales (%)", "in_app": False},
        {"id": "comp_amb_extractiva", "col": "P026_2019_2022_2024", "type": "target_pct", "target": 1.0, "title": "Afectado por Industrias extractivas (salmoneras, minería, forestal) (%)", "in_app": False},
        {"id": "comp_amb_biodiversidad", "col": "P027_2019_2022_2024", "type": "target_pct", "target": 1.0, "title": "Afectado por Pérdida de flora, fauna y bosques (%)", "in_app": False},
        {"id": "comp_amb_energia", "col": "P028_2019_2022_2024", "type": "target_pct", "target": 1.0, "title": "Afectado por Proyectos energéticos / hidroeléctricos (%)", "in_app": False},
        {"id": "comp_amb_cambio_clim", "col": "P029_2019_2022_2024", "type": "target_pct", "target": 1.0, "title": "Afectado por Efectos del Cambio Climático (%)", "in_app": False}
    ],
    "Módulo 7: Consumo de Medios de Comunicación y Dieta Informativa": [
        {"id": "comp_medios_tv_nac", "col": "P030_2024", "type": "target_pct", "target": 1.0, "title": "Uso de Canales de TV Nacionales (%)", "in_app": False},
        {"id": "comp_medios_tv_loc", "col": "P031_2024", "type": "target_pct", "target": 1.0, "title": "Uso de Canales de TV Locales / Regionales (%)", "in_app": False},
        {"id": "comp_medios_rad_nac", "col": "P032_2024", "type": "target_pct", "target": 1.0, "title": "Uso de Radios Nacionales (%)", "in_app": False},
        {"id": "comp_medios_rad_loc", "col": "P033_2024", "type": "target_pct", "target": 1.0, "title": "Uso habitual de Radios Locales / Comunitarias (%)", "in_app": False},
        {"id": "comp_medios_prensa", "col": "P034_2024", "type": "target_pct", "target": 1.0, "title": "Uso de Diarios o Prensa Escrita Regional (%)", "in_app": False},
        {"id": "comp_medios_online", "col": "P035_2024", "type": "target_pct", "target": 1.0, "title": "Uso de Portales de Noticias Digitales Regionales (%)", "in_app": False},
        {"id": "comp_medios_rrss", "col": "P036_2024", "type": "target_pct", "target": 1.0, "title": "Uso de Redes Sociales (Facebook, WhatsApp, Instagram) (%)", "in_app": False},
        {"id": "comp_medios_principal", "col": "P037_2024", "type": "full_dist", "title": "Medio de Comunicación PRINCIPAL para informarse (%)", "in_app": True}
    ],
    "Módulo 8: Fortalezas Regionales y Planificación": [
        {"id": "comp_fortaleza_1", "col": "P038_2019_2022_2024", "type": "full_dist", "title": "Principal fortaleza o ventaja de la región (%)", "in_app": False},
        {"id": "comp_fortaleza_2", "col": "P039_2019_2022_2024", "type": "full_dist", "title": "Segunda fortaleza o ventaja de la región (%)", "in_app": False},
        {"id": "comp_conocimiento_erd", "col": "P040_2024", "type": "target_pct", "target": 1.0, "title": "Conocimiento de la Estrategia Regional de Desarrollo (ERD) (%)", "in_app": False}
    ],
    "Módulo 9: Aporte al Desarrollo Regional de Instituciones y Actores (% Mucho + Algo)": [
        {"id": "comp_inst_gob_central", "col": "P041_2019_2022_2024", "type": "target_pct", "target": 1.0, "title": "Aporte del Gobierno Central (%)", "in_app": False},
        {"id": "comp_inst_gore", "col": "P042_2019_2022_2024", "type": "target_pct", "target": 1.0, "title": "Aporte del Gobierno Regional (GORE) (%)", "in_app": False},
        {"id": "comp_inst_municipio", "col": "P043_2019_2022_2024", "type": "target_pct", "target": 1.0, "title": "Aporte de las Municipalidades (%)", "in_app": False},
        {"id": "comp_inst_empresas", "col": "P044_2019_2022_2024", "type": "target_pct", "target": 1.0, "title": "Aporte de las Empresas Privadas Regionales (%)", "in_app": False},
        {"id": "comp_inst_parlamentarios", "col": "P045_2019_2022_2024", "type": "target_pct", "target": 1.0, "title": "Aporte de Diputados y Senadores (%)", "in_app": False},
        {"id": "comp_inst_org_sociales", "col": "P046_2019_2022_2024", "type": "target_pct", "target": 1.0, "title": "Aporte de Organizaciones Comunitarias / Sociales (%)", "in_app": False},
        {"id": "comp_inst_universidades", "col": "P047_2024", "type": "target_pct", "target": 1.0, "title": "Aporte de las Universidades Regionales (%)", "in_app": False},
        {"id": "comp_inst_medios_loc", "col": "P048_2019_2022_2024", "type": "target_pct", "target": 1.0, "title": "Aporte de los Medios de Comunicación Regionales (%)", "in_app": False}
    ],
    "Módulo 10: Descentralización y Decisión Territorial (% Debería ser Regional o Local)": [
        {"id": "comp_dec_salud", "col": "P049_2019_2022_2024", "type": "full_dist", "title": "Decisión sobre Salud Pública (Nacional vs Regional vs Comunal)", "in_app": False},
        {"id": "comp_dec_educacion", "col": "P050_2019_2022_2024", "type": "full_dist", "title": "Decisión sobre Educación Pública (Nacional vs Regional vs Comunal)", "in_app": False},
        {"id": "comp_dec_agua", "col": "P051_2019_2022_2024", "type": "full_dist", "title": "Decisión sobre Administración del Agua (Nacional vs Regional vs Comunal)", "in_app": False},
        {"id": "comp_dec_vivienda", "col": "P052_2019_2022_2024", "type": "full_dist", "title": "Decisión sobre Vivienda y Urbanismo (Nacional vs Regional vs Comunal)", "in_app": False},
        {"id": "comp_dec_medioambiente", "col": "P053_2019_2022_2024", "type": "full_dist", "title": "Decisión sobre Protección del Medioambiente (Nacional vs Regional vs Comunal)", "in_app": False},
        {"id": "comp_dec_obras", "col": "P054_2019_2022_2024", "type": "full_dist", "title": "Decisión sobre Grandes Obras de Infraestructura (Nacional vs Regional vs Comunal)", "in_app": False},
        {"id": "comp_dec_inversion", "col": "P055_2019_2022_2024", "type": "full_dist", "title": "Decisión sobre Localización de Grandes Proyectos (Nacional vs Regional vs Comunal)", "in_app": False},
        {"id": "comp_dec_seguridad", "col": "P056_2019_2022_2024", "type": "full_dist", "title": "Decisión sobre Seguridad y Orden Público (Nacional vs Regional vs Comunal)", "in_app": False},
        {"id": "comp_dec_fomento", "col": "P057_2019_2022_2024", "type": "full_dist", "title": "Decisión sobre Fomento Productivo (Nacional vs Regional vs Comunal)", "in_app": False},
        {"id": "comp_impacto_gobernadores", "col": "P059_2019_2022_2024", "type": "full_dist", "title": "Impacto de la Elección Directa de Gobernadores Regionales (%)", "in_app": False}
    ],
    "Módulo 11: Actitudes hacia la Democracia y Política": [
        {"id": "comp_democracia_apoyo", "col": "P073_2019_2022_2024", "type": "full_dist", "title": "Apoyo a la Democracia vs Autoritarismo vs Indiferencia (%)", "in_app": False},
        {"id": "comp_posicion_politica", "col": "P074_2019_2022_2024", "type": "full_dist", "title": "Autoidentificación Política (Izquierda, Centro, Derecha, Indep) (%)", "in_app": False}
    ],
    "Módulo 12: Demografía Comparada y Brechas Capital/Provincias": [
        {"id": "comp_demo_gse", "col": "GSE_2019_2022_2024", "type": "full_dist", "title": "Estructura Socioeconómica (GSE ABC1/C2/C3/D/E) por Región (%)", "in_app": False},
        {"id": "comp_demo_edad", "col": "Edad_2019_2022_2024", "type": "mean", "title": "Edad promedio y pirámide etaria por Región", "in_app": False},
        {"id": "comp_demo_capital_resto", "col": "Capital_2019_2022_2024", "type": "full_dist", "title": "Distribución Poblacional Capital Regional vs Provincias/Otras Comunas (%)", "in_app": False}
    ]
}

computed_catalog = []
total_possible = 0
implemented_count = 0

for mod_name, items in modules.items():
    mod_data = {"module": mod_name, "charts": []}
    for item in items:
        total_possible += 1
        if item['in_app']:
            implemented_count += 1
        
        col = item['col']
        t = item['type']
        target = item.get('target', None)
        
        reg_vals = calc_regional_metric(col, t, target)
        
        mod_data["charts"].append({
            "id": item["id"],
            "title": item["title"],
            "col": col,
            "type": t,
            "target": target,
            "in_app": item["in_app"],
            "regional_values": reg_vals
        })
    computed_catalog.append(mod_data)

with open(r"C:\AGY\BAROMETRO\scripts\computed_comparative_catalog.json", "w", encoding="utf-8") as f:
    json.dump(computed_catalog, f, ensure_ascii=False, indent=2)

print(f"Total possible regional comparison charts: {total_possible}")
print(f"Currently implemented in app: {implemented_count}")
print(f"Missing / Potential charts to build: {total_possible - implemented_count}")

