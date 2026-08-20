import sys
sys.stdout.reconfigure(encoding='utf-8')

import re
import json

with open(r"C:\AGY\BAROMETRO\index.html", "r", encoding="utf-8") as f:
    html = f.read()

with open(r"C:\AGY\BAROMETRO\scripts\all_charts_detailed.json", "r", encoding="utf-8") as f:
    charts = json.load(f)

# Descriptions for all 41 charts
descriptions = {
    # RESUMEN
    "chart-rumbo-canvas": {
        "title": "Evaluación del Rumbo de la Región (B1)",
        "badge": "Evaluación de Coyuntura",
        "desc": "Muestra la percepción ciudadana sobre la trayectoria actual de la Región de Aysén: si la región está progresando, estancada o en decadencia."
    },
    "chart-problemas-canvas": {
        "title": "Principales Problemas Regionales Percibidos (B2)",
        "badge": "Principales Preocupaciones",
        "desc": "Ranking de las principales problemáticas que afectan a la región según los encuestados (conectividad/aislamiento, salud, costo de la vida, empleo, vivienda, etc.)."
    },
    "chart-servicios-completo-canvas": {
        "title": "Evaluación Detallada de Calidad de Vida y Servicios (B3 y B4)",
        "badge": "Calidad de Vida & Infraestructura",
        "desc": "Evaluación en escala de notas escolares (1.0 a 7.0) de 12 dimensiones: recreación, empleo, educación, remuneraciones, participación ciudadana, seguridad, calidad ambiental, caminos/conectividad, salud pública, transporte público, acceso a vivienda y conectividad a internet."
    },
    
    # IDENTIDAD
    "chart-pertenencia-canvas": {
        "title": "Sentido de Pertenencia Territorial Principal (A1)",
        "badge": "Identidad Territorial",
        "desc": "Nivel territorial con el que los habitantes se sienten más identificados en primer lugar (Barrio, Pueblo/Localidad, Comuna, Ciudad, Región o País)."
    },
    "chart-servicios-canvas": {
        "title": "Evaluación de Servicios Básicos Regionales (B4)",
        "badge": "Calidad de Vida",
        "desc": "Calificación promedio (escala de notas 1.0 a 7.0) de los servicios esenciales: conectividad vial, salud pública, transporte, vivienda e internet."
    },
    "chart-movilidad-canvas": {
        "title": "Disposición a Migrar / Cambiarse de Residencia (A2)",
        "badge": "Movilidad & Retención",
        "desc": "Porcentaje de personas a quienes les gustaría cambiarse de residencia o irse a vivir a otro lugar si dependiera de ellos."
    },
    "chart-destino-canvas": {
        "title": "Destino Preferido de Migración (A3)",
        "badge": "Destino Preferido",
        "desc": "Lugar preferido al que desearían mudarse quienes manifiestan disposición a migrar (dentro de la misma comuna, a otra comuna de Aysén, a otra región de Chile o al extranjero)."
    },
    
    # GOBERNANZA
    "chart-gobernanza-canvas": {
        "title": "¿Quién debería tomar las decisiones públicas? (G1)",
        "badge": "Toma de Decisiones",
        "desc": "Distribución porcentual de preferencia de decisión (Autoridades Nacionales vs Regionales vs Comunales) en 9 áreas: Salud, Educación, Agua, Vivienda, Medioambiente, Obras Públicas, Inversiones, Seguridad y Fomento Productivo."
    },
    "chart-instituciones-canvas": {
        "title": "Aporte al Desarrollo Regional de Actores e Instituciones (F4)",
        "badge": "Aporte de Actores",
        "desc": "Porcentaje de evaluación positiva (% Mucho + Algo) del aporte de 8 entidades clave: Gobierno Central, GORE, Municipalidades, Empresas Regionales, Parlamentarios, Organizaciones Sociales, Universidades y Medios de Comunicación."
    },
    "chart-medio-principal-canvas": {
        "title": "Medio de Comunicación Principal para Informarse (E2)",
        "badge": "Ecología de Medios",
        "desc": "Medio prioritario que utiliza la ciudadanía para mantenerse informada de la contingencia regional (Radios locales, TV nacional, Redes sociales, Portales web, Diarios locales, TV local)."
    },
    "chart-centralismo-canvas": {
        "title": "Percepción de Relación frente a Santiago / Centralismo (G2)",
        "badge": "Autonomía Regional",
        "desc": "Percepción sobre si ha aumentado el centralismo y la dependencia frente a Santiago, o si existe mayor autonomía de la región."
    },
    "chart-gobernadores-canvas": {
        "title": "Impacto de la Elección Directa de Gobernadores Regionales (G3)",
        "badge": "Descentralización Política",
        "desc": "Evaluación del impacto del traspaso de competencias y la figura del Gobernador Regional (ha sido un impulso, ha dejado las cosas igual, o ha traído problemas)."
    },
    "chart-democracia-canvas": {
        "title": "Actitudes hacia la Democracia y el Gobierno (H1)",
        "badge": "Cultura Democrática",
        "desc": "Adhesión al régimen democrático: porcentaje que considera la democracia preferible a cualquier otra forma de gobierno, frente al autoritarismo o la indiferencia política."
    },
    "chart-posicion-politica-canvas": {
        "title": "Autoidentificación Política en la Región (H2)",
        "badge": "Identificación Política",
        "desc": "Distribución de los encuestados en el eje político: Izquierda, Centro-Izquierda, Centro, Centro-Derecha, Derecha, e Independiente / Sin identificación."
    },
    
    # MEDIOAMBIENTE
    "chart-ambiental-canvas": {
        "title": "Priorización entre Desarrollo Económico y Protección Ambiental (D1)",
        "badge": "Sustentabilidad",
        "desc": "Postura ciudadana respecto a privilegiar el cuidado del medioambiente y los recursos naturales versus impulsar el crecimiento de la actividad económica."
    },
    "chart-economia-canvas": {
        "title": "Percepción del Impacto de Industrias Productivas (D2)",
        "badge": "Matriz Productiva",
        "desc": "Evaluación del aporte económico y laboral versus los costos ambientales generados por sectores como la salmonicultura, turismo, ganadería y energía."
    },
    "chart-afectacion-ambiental-canvas": {
        "title": "Conflictos Socioambientales y Afectación Directa (D1_A a D1_G)",
        "badge": "Impacto Ambiental Percibido",
        "desc": "Porcentaje de hogares que se han sentido afectados directamente por 7 problemáticas: contaminación del aire/humo de leña, escasez de agua, basura y vertederos, salmoneras/minería, pérdida de biodiversidad, proyectos energéticos y cambio climático."
    },
    "chart-salmon-impactos-canvas": {
        "title": "Percepción sobre un Escenario sin Industria del Salmón (I2)",
        "badge": "Escenario Salmonicultura",
        "desc": "Grado de acuerdo frente a los impactos en Aysén si cesara la industria salmonera: empleo, economía regional y recuperación ambiental de los fiordos."
    },
    "chart-turismo-mitos-canvas": {
        "title": "Percepción sobre el Potencial y Desarrollo Turístico (I3)",
        "badge": "Desarrollo Turístico",
        "desc": "Opinión sobre si el turismo puede reemplazar la matriz extractiva, estado de la infraestructura turística regional y sostenibilidad."
    },
    
    # UAYSEN
    "chart-uaysen-aporte-canvas": {
        "title": "Evaluación del Aporte de la Universidad de Aysén al Desarrollo Regional (I4)",
        "badge": "Impacto Regional",
        "desc": "Evaluación cuantitativa en nota de 1.0 a 7.0 y nivel de aprobación ciudadana sobre la labor académica, formativa y territorial de la UAysén."
    },
    "chart-uaysen-cualitativo-canvas": {
        "title": "Asociación y Percepción Cualitativa Espontánea de la UAysén (I51)",
        "badge": "Percepción Cualitativa",
        "desc": "Categorización de las menciones y conceptos espontáneos con los que la comunidad asocia a la Universidad de Aysén (oportunidad para jóvenes, crisis institucional, descentralización, etc.)."
    },
    
    # CONFIANZA
    "chart-confianza-canvas": {
        "title": "Nivel de Confianza Interpersonal Generalizada (C1)",
        "badge": "Confianza Generalizada",
        "desc": "Porcentaje de personas que afirma que 'se puede confiar en la mayoría de las personas' frente a la postura de que 'uno nunca es lo suficientemente cuidadoso'."
    },
    "chart-participacion-canvas": {
        "title": "Participación en Organizaciones Comunitarias y Sociales (C2)",
        "badge": "Participación Comunitaria",
        "desc": "Porcentaje de participación activa y tipo de organizaciones en las que participa la ciudadanía (juntas de vecinos, clubes deportivos, comités de vivienda, colectivos culturales, etc.)."
    },
    
    # DEMOGRAFIA
    "chart-educacion-canvas": {
        "title": "Nivel Educacional de la Muestra (J1)",
        "badge": "Escolaridad",
        "desc": "Distribución del máximo nivel de estudios alcanzado por los encuestados (Básica, Media Científico-Humanista, Media Técnico-Profesional, Técnica Superior, Universitaria y Postgrados)."
    },
    "chart-gse-canvas": {
        "title": "Estratificación Socioeconómica (GSE)",
        "badge": "Nivel Socioeconómico",
        "desc": "Distribución de los hogares según la matriz estandarizada de grupos socioeconómicos (ABC1, C2, C3, D, E)."
    },
    "chart-ocupacion-canvas": {
        "title": "Estructura Ocupacional y Situación Laboral (J3 / CIUO08)",
        "badge": "Fuerza de Trabajo",
        "desc": "Distribución de los jefes/as de hogar por ramas y categorías de ocupación (trabajadores por cuenta propia, empleados sector público, sector privado, jubilados, etc.)."
    },
    
    # COMPARATIVA INTERREGIONAL
    "chart-comp-pertenencia": {
        "title": "Territorio de Pertenencia Prioritario por Región (%)",
        "badge": "Identidad Territorial Interregional",
        "desc": "Barras apiladas al 100% que comparan el apego identitario (Barrio, Pueblo, Comuna, Ciudad, Región, País) en las 7 regiones del Barómetro."
    },
    "chart-comp-migrar": {
        "title": "Disposición a Migrar / Irse de la Región (%)",
        "badge": "Movilidad Humana Interregional",
        "desc": "Ranking comparativo de disposición al éxodo territorial entre O'Higgins, Ñuble, Biobío, Los Ríos, Los Lagos, Aysén y Magallanes."
    },
    "chart-comp-rumbo": {
        "title": "Rumbo Regional Completo: Progresando vs Estancada vs Decadencia (%)",
        "badge": "Rumbo Regional Completo",
        "desc": "Barras apiladas al 100% con la evaluación de marcha y dinamismo de cada una de las 7 regiones."
    },
    "chart-comp-estancamiento": {
        "title": "Percepción de Estancamiento por Región (%)",
        "badge": "Benchmark Estancamiento",
        "desc": "Ranking interregional del porcentaje de población que percibe su territorio como 'estancado' (Aysén en 1° lugar con 57.7%)."
    },
    "chart-comp-problemas": {
        "title": "Principal Problema Percibido en la Región (%)",
        "badge": "Diagnóstico Temático Interregional",
        "desc": "Barras apiladas con los principales problemas declarados en cada territorio (Seguridad, Infraestructura/Conectividad, Salud, Empleo, Economía, Otros)."
    },
    "chart-comp-fortalezas": {
        "title": "Principal Fortaleza Percibida de la Región (%)",
        "badge": "Potencial y Recursos Regionales",
        "desc": "Barras apiladas que comparan las mayores ventajas percibidas (Riquezas naturales, Capacidad de trabajo, Empresarios, Profesionales, etc.) en las 7 regiones."
    },
    "chart-comp-gob-central": {
        "title": "Aporte del Gobierno Central al Desarrollo Regional (%)",
        "badge": "Aporte Nivel Central",
        "desc": "Ranking de aprobación (% Mucho + Algo) del aporte del Ejecutivo nacional en las 7 regiones evaluadas."
    },
    "chart-comp-gore": {
        "title": "Aporte del Gobierno Regional (GORE) (%)",
        "badge": "Aporte Nivel Regional",
        "desc": "Ranking de aprobación (% Mucho + Algo) de la gestión y aporte de los Gobiernos Regionales."
    },
    "chart-comp-municipios": {
        "title": "Aporte de las Municipalidades (%)",
        "badge": "Aporte Nivel Local",
        "desc": "Ranking de evaluación positiva (% Mucho + Algo) de los gobiernos locales en cada región."
    },
    "chart-comp-democracia": {
        "title": "Apoyo a la Democracia vs Autoritarismo (%)",
        "badge": "Cultura Democrática Interregional",
        "desc": "Barras apiladas al 100% que comparan la valoración de la democracia a todo evento frente a posturas autoritarias o indiferentes en las 7 regiones."
    },
    "chart-comp-pos-politica": {
        "title": "Autoidentificación Política en el Territorio (%)",
        "badge": "Espectro Político Interregional",
        "desc": "Barras apiladas con la distribución del espectro político (Izquierda, Centro, Derecha, Independientes) en las 7 regiones."
    },
    "chart-comp-confianza": {
        "title": "Confianza Interpersonal por Región (%)",
        "badge": "Cohesión Social Interregional",
        "desc": "Ranking de confianza interpersonal donde Aysén (45.8%) y Magallanes (52.6%) destacan ampliamente sobre el centro-sur del país (25-28%)."
    },
    "chart-comp-centralismo": {
        "title": "Percepción de Aumento del Centralismo frente a Santiago (%)",
        "badge": "Autonomía Territorial",
        "desc": "Ranking comparativo donde Aysén registra el mayor malestar por dependencia centralista con un 57%."
    },
    "chart-comp-seguridad": {
        "title": "Evaluación de Seguridad Ciudadana (Nota 1.0 a 7.0)",
        "badge": "Evaluación Sectorial",
        "desc": "Comparativa de notas promedio otorgadas al combate a la delincuencia y orden público en cada región."
    },
    "chart-comp-radios": {
        "title": "Uso Prioritario de Radios Locales / Comunitarias (%)",
        "badge": "Ecología de Medios",
        "desc": "Ranking comparativo del consumo de radios locales como fuente primaria informativa (Aysén líder con 18%)."
    }
}

print(f"Total documented charts: {len(descriptions)}")
