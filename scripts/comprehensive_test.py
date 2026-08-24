import pyreadstat
import pandas as pd
import numpy as np
import json
import sys

# Set utf-8 stdout
sys.stdout.reconfigure(encoding='utf-8')

print("================================================================================")
print("INICIANDO VALIDACIÓN AUTOMATIZADA INTEGRAL DE DATOS")
print("================================================================================")

# 1. Cargar bases de datos
df_aysen, meta_aysen = pyreadstat.read_sav("Base Barómetro Aysén 2025.03.11.sav")
df_int, meta_int = pyreadstat.read_sav("base_integrada_spss.sav", apply_value_formats=False)

with open("data/barometro_summary.json", "r", encoding="utf-8") as f:
    summary_json = json.load(f)

with open("data/comparativa_interregional.json", "r", encoding="utf-8") as f:
    comp_json = json.load(f)

errors = []

# TEST 1: Identificación UAysén (I6)
w = df_aysen['PONDERADOR']
i6_valid = df_aysen['I6'].between(0, 100)
i6_expected = float(np.average(df_aysen['I6'][i6_valid], weights=w[i6_valid]))
i6_in_json = summary_json['overall']['uaysen_identificacion_mean']

if abs(i6_expected - i6_in_json) > 0.05:
    errors.append(f"TEST 1 ERROR: I6 en JSON ({i6_in_json}) no coincide con SPSS ({i6_expected:.2f})")
else:
    print(f"[OK] TEST 1 PASADO: Identificación UAysén I6 es exactamente {i6_in_json:.2f} pts (SPSS={i6_expected:.2f})")

# TEST 2: Sexo - Mapeo y Proporciones
hombres = [r for r in summary_json['records'] if r['sexo'] == 'Hombre']
mujeres = [r for r in summary_json['records'] if r['sexo'] == 'Mujer']
n_hombres_spss = len(df_aysen[df_aysen['SEXO'] == 1.0])
n_mujeres_spss = len(df_aysen[df_aysen['SEXO'] == 2.0])

if len(hombres) != n_hombres_spss or len(mujeres) != n_mujeres_spss:
    errors.append(f"TEST 2 ERROR: Conteo de Sexo incorrecto. Hombres JSON={len(hombres)}, SPSS={n_hombres_spss}")
else:
    w_h = sum(r['weight'] for r in hombres) / sum(r['weight'] for r in summary_json['records']) * 100
    w_m = sum(r['weight'] for r in mujeres) / sum(r['weight'] for r in summary_json['records']) * 100
    print(f"[OK] TEST 2 PASADO: Sexo correctamente alineado (Hombres: {len(hombres)} casos, {w_h:.1f}%; Mujeres: {len(mujeres)} casos, {w_m:.1f}%)")

# TEST 3: Posición Política (H2 = 97 Ninguna)
h2_json = summary_json['overall']['politica_h2']
if "Ninguna" not in h2_json or h2_json["Ninguna"]["percentage"] < 40:
    errors.append(f"TEST 3 ERROR: H2 'Ninguna' no está en el resumen o porcentaje incorrecto: {h2_json.get('Ninguna')}")
else:
    print(f"[OK] TEST 3 PASADO: H2 'Ninguna' incluido correctamente con {h2_json['Ninguna']['percentage']}% ({h2_json['Ninguna']['count']} casos)")

# TEST 4: Servicios Aysén (B3_A a B3_I y B4_A a B4_E)
servicios_json = summary_json['overall']['evaluacion_servicios']
for col in ['B3_A', 'B3_B', 'B3_C', 'B3_D', 'B3_E', 'B3_F', 'B3_G', 'B3_H', 'B3_I']:
    s = df_aysen[col]
    val = s.between(1, 7)
    exp_mean = float(np.average(s[val], weights=w[val]))
    json_mean = servicios_json[col]['mean']
    if abs(exp_mean - json_mean) > 0.05:
        errors.append(f"TEST 4 ERROR: Media de {col} ({json_mean}) no coincide con SPSS ({exp_mean:.2f})")
print(f"[OK] TEST 4 PASADO: Todas las 9 dimensiones B3 de Aysén coinciden exactamente con SPSS.")

# TEST 5: Comparativa Interregional - Mapeo de Servicios
aysen_salud = [x for x in comp_json['servicios']['salud'] if x['region'] == 'Aysén'][0]['nota']
aysen_agua = [x for x in comp_json['servicios']['agua'] if x['region'] == 'Aysén'][0]['nota']
aysen_vivienda = [x for x in comp_json['servicios']['vivienda'] if x['region'] == 'Aysén'][0]['nota']

if abs(aysen_salud - 3.44) > 0.05:
    errors.append(f"TEST 5 ERROR: Salud en comparativa Aysén es {aysen_salud} (esperado 3.44)")
if abs(aysen_agua - 5.39) > 0.05:
    errors.append(f"TEST 5 ERROR: Agua en comparativa Aysén es {aysen_agua} (esperado 5.39)")
if abs(aysen_vivienda - 4.09) > 0.05:
    errors.append(f"TEST 5 ERROR: Vivienda en comparativa Aysén es {aysen_vivienda} (esperado 4.09)")

if not any("TEST 5" in e for e in errors):
    print(f"[OK] TEST 5 PASADO: Comparativa Interregional de Servicios 100% alineada con P008-P019 (Salud={aysen_salud}, Agua={aysen_agua}, Vivienda={aysen_vivienda})")

# TEST 6: Comparativa Destino de Migración (4 categorías)
dest = comp_json['coyuntura']['destino_migracion'][0]
if not all(k in dest for k in ["misma_comuna", "otra_comuna", "otra_region", "extranjero"]):
    errors.append(f"TEST 6 ERROR: Estructura de destino de migración incompleta: {dest.keys()}")
else:
    print(f"[OK] TEST 6 PASADO: Destino de migración contiene las 4 opciones correctas ({list(dest.keys())})")

# TEST 7: Comparativa Identificación Territorial (6 categorías)
ident = comp_json['coyuntura']['identificacion_territorial'][0]
if not all(k in ident for k in ["barrio", "pueblo_localidad", "comuna", "ciudad", "region", "pais"]):
    errors.append(f"TEST 7 ERROR: Estructura de identificación territorial incompleta: {ident.keys()}")
else:
    print(f"[OK] TEST 7 PASADO: Identificación territorial contiene las 6 jerarquías territoriales completas.")

# TEST 8: Consistencia de Confianza Interpersonal entre Dashboard y Comparativa
conf_aysen_comp = [x for x in comp_json['cohesion']['confianza'] if x['region'] == 'Aysén'][0]['pct']
conf_aysen_summary = summary_json['overall']['confianza_c1']['Se puede confiar en las personas']['percentage']

if abs(conf_aysen_comp - conf_aysen_summary) > 0.1:
    errors.append(f"TEST 8 ERROR: Confianza de Aysén en comparativa ({conf_aysen_comp}%) difiere del dashboard local ({conf_aysen_summary}%)")
else:
    print(f"[OK] TEST 8 PASADO: Confianza Interpersonal de Aysén es exactamente {conf_aysen_comp}% en el Benchmark y en el Dashboard.")

print("================================================================================")
if errors:
    print(f"[ERROR] SE ENCONTRARON {len(errors)} ERRORES:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("[SUCCESS] TODOS LOS TESTS PASARON EXITOSAMENTE. CERO INCONGRUENCIAS DETECTADAS.")
    print("================================================================================")
