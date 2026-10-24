# QGIS Testing & Santa Cruz de Tenerife Urban Planning (PGOU)

Automated GIS workflow, symbology, and cartographic layout generation for urban planning in Santa Cruz de Tenerife, Canary Islands.

---

## 📌 Project Overview

This repository contains PyQGIS scripts, map project configurations, layer styles, and automation tools for processing and presenting urban and rural land classification (PGOU) data for Santa Cruz de Tenerife.

### Core Features
- **Hierarchical Symbology**: Automated styling of the `CLA` (Clasificación de Suelo) layer based on official planning codes (`color_ref.csv`), structured into 5 superclasses:
  1. *Suelo Urbano* (`SUCO`, `SUNCO`, `SUC-IC`)
  2. *Suelo Urbanizable* (`SUSO`, `SUS`, `SUSNO`, `SUNS`, `SUNSE`, `SUNSD`)
  3. *Suelo Rústico - Ambiental y Territorial* (`SRPN`, `SRPP`, `SRPT-AL`, `SRPT-AT`)
  4. *Suelo Rústico - Productivo y Asentamientos* (`SRPA`, `SRAR`, `SRPM`)
  5. *Suelo Rústico - Redes y Sectorial* (`SRPH`, `SRPC`, `SRPI`)
- **Grouped Legend Print Layouts**: Automated generation of publication-quality A4 landscape maps featuring decoupled, grouped legends (Urban in upper-left, Rural in lower-right), scale bars, north arrows, and custom title blocks.
- **Geolocated Photo Layouts**: Automatic extraction of GPS coordinates from site photos with leader lines connecting photo frames to exact ground locations.

---

## 📁 Repository Structure

```text
QGIS-testing/
├── config/
│   └── color_ref.csv          # Color palette, opacity, and hierarchy for PGOU categories
├── data/
│   └── Santa Cruz de Tenerife/ # Vector layers, QLR layer definitions, and shapefiles
├── output/
│   ├── Plano_Clasificacion_Suelo_A4.pdf  # Vector PDF print map
│   └── Plano_Clasificacion_Suelo_A4.png  # High-resolution raster preview
├── QGIS_projects/
│   └── Santa Cruz de Tenerife/ # Active QGIS project file (.qgz)
├── QGIS_scripts/
│   ├── qgis_apply_hierarchical_style.py  # Builds rule-based symbology from CSV
│   ├── qgis_create_grouped_legend_layout.py # Builds A4 layout with split legends
│   └── qgis_create_photo_layout.py       # Builds photo layout with leader lines
├── AGENTS.md                  # Environment paths, CLI tools & AI agent instructions
└── README.md                  # Project documentation (this file)
```

---

## 🚀 How to Run the Scripts

### Option A: From QGIS Desktop (Interactive)
1. Open QGIS Desktop and load the project:
   `QGIS_projects/Santa Cruz de Tenerife/Santa Cruz de Tenerife.qgz`
2. Open the Python Console (`Ctrl + Alt + P`) -> **Show Editor**.
3. Open any script from `QGIS_scripts/` (e.g., `qgis_create_grouped_legend_layout.py`) and click **Run**.
4. The layout will be generated, saved to the project, exported to `output/`, and displayed in the Layout Designer.

### Option B: Standalone / Headless (via OSGeo4W)
Scripts can be executed completely outside the GUI using the OSGeo4W PyQGIS batch runner:
```powershell
C:\OSGeo4W\bin\python-qgis-ltr.bat QGIS_scripts\qgis_create_grouped_legend_layout.py
```

---

## 🔗 External Resources & References
- [Planes Insulares de Ordenación (datos.gob.es)](https://datos.gob.es/es/catalogo/a05003638-planes-insulares-de-ordenacion)
- [IDECanarias WMS & Spatial Data](https://www.idecanarias.es/)
- Technical agent environment settings, OSGeo4W suite command list, and runtime variables are documented in [AGENTS.md](file:///c:/dev/QGIS-testing/AGENTS.md).