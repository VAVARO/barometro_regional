# Barómetro Regional Universidad de Aysén

Dashboard interactivo moderno y responsive para la visualización de datos del **Barómetro Regional de la Universidad de Aysén 2025**.

## Estructura del Proyecto

```
barometro_regional/
├── index.html                  # Aplicación principal SPA (HTML5 + Tailwind CSS)
├── css/
│   └── styles.css              # Estilos personalizados, cristalografía y animaciones
├── js/
│   └── app.js                  # Motor interactivo, filtros ponderados y renderizado Chart.js
├── data/
│   └── barometro_summary.json  # Dataset pre-procesado en UTF-8 con ponderaciones y microdatos
└── scripts/
    ├── build_data.py           # Extracción y limpieza desde SPSS .sav
    └── fix_encoding.py         # Normalización de caracteres UTF-8
```

## Características
- **Filtros Dinámicos:** Selección por Comuna, Zona (Urbana/Rural), Rango Etario y Nivel Socioeconómico (GSE).
- **KPIs & Gráficos Interactivos:** Progresión regional, prioridades públicas, identidad territorial, autonomía decisional y evaluación de la Universidad de Aysén.
- **Explorador Data Intelligence:** Generador de tablas de contingencia cruzada (crosstab) con descarga en formato CSV.
- **Diseño Responsive:** Optimizado para escritorio y dispositivos móviles siguiendo los lineamientos de Patagonian Data Intelligence.

## Desarrollo Local
Para ejecutar localmente sin dependencias externas:
1. Clonar el repositorio.
2. Iniciar un servidor HTTP estático en la raíz del proyecto:
   ```bash
   python -m http.server 8080
   ```
3. Abrir `http://localhost:8080/index.html` en el navegador.
