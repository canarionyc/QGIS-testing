# Log de Logros: Generación de Plano A4 con Leyendas Agrupadas (PyQGIS)

**Fecha:** 2026-10-23 / 2026-11-09  
**Proyecto:** Plan General de Ordenación - Santa Cruz de Tenerife  
**Ubicación:** `c:\dev\QGIS-testing`  
**Script principal:** [`qgis_create_grouped_legend_layout.py`](file:///c:/dev/QGIS-testing/QGIS_scripts/qgis_create_grouped_legend_layout.py)  

---

## 1. Objetivo y Alcance

Automatizar la composición e impresión de un plano cartográfico en formato **A4 Horizontal (Landscape)** con la capa de Clasificación del Suelo (`CLA`), organizando la simbología en **dos bloques de leyendas independientes**:
1. **Esquina Superior Izquierda:** Superclases 1 (*Suelo Urbano*) y 2 (*Suelo Urbanizable*).
2. **Esquina Inferior Derecha:** Superclases 3, 4 y 5 (*Suelo Rústico - Ambiental/Territorial, Productivo/Asentamientos, Redes y Sectorial*).

Aprovechando las zonas vacías del encuadre (mar y áreas no urbanas) para mantener despejado el tejido urbano central.

---

## 2. Hitos Técnicos Alcanzados

### 2.1. Partición Dinámica de Reglas de Simbología (`partition_legend_node_indices`)
- Inspección directa del `rootRule` del `QgsRuleBasedRenderer` de la capa `CLA`.
- Detección automática de los prefijos de las supercategorías (`1.`, `2.`, `3.`, `4.`, `5.`) sin recurrir a índices fijos o dependencias rígidas de base de datos.
- Agrupación precisa de los nodos hijos (símbolos) y padres (títulos de grupo).

### 2.2. Aislamiento y Control de Nodos en la Leyenda (`create_styled_legend`)
- **Limpieza de C++ Tree:** Se utilizó `legend.model().rootGroup().clear()` y `root.addLayer(layer)` para garantizar estabilidad de punteros Qt/C++ sin fugas de memoria o cuelgues del proceso.
- **Ocultación del encabezado de capa:** `QgsLegendRenderer.setNodeLegendStyle(layer_node, QgsLegendStyle.Hidden)` para evitar títulos redundantes y dejar visibles únicamente las clases temáticas.
- **Filtrado selectivo:** `QgsMapLayerLegendUtils.setLegendNodeOrder()` junto con `legend.model().refreshLayerLegend()` para materializar solo las categorías de cada bloque.

### 2.3. Tipografía y Estilo de Tarjeta Cartográfica
- Integración de `QgsTextFormat` con tipografía *Segoe UI* estructurada jerárquicamente:
  - Títulos de tarjeta: 8 pt Negrita (`#1a237e`).
  - Grupos de superclase: 7 pt Negrita (`#263238`).
  - Subclases/Símbolos: 6 pt Regular (`#37474f`).
- Tarjetas con fondo blanco translúcido (`rgba(255, 255, 255, 240)`), borde gris arquitectónico (`#b0bec5`, grosor 0.25 mm) y espaciado compacto optimizado para formato A4.

### 2.4. Composición de Elementos Auxiliares
- **Cajetín / Título Superior Izquierdo:** `QgsLayoutItemShape` + `QgsLayoutItemLabel` vinculados sobre la leyenda 1 con títulos normalizados (*"PLAN GENERAL DE ORDENACIÓN · Santa Cruz de Tenerife"*).
- **Barra de Escala:** `QgsLayoutItemScaleBar` configurada en kilómetros (segmentos de 1 km), con caja de fondo protectora contra el ortofoto.
- **Flecha Norte:** `QgsLayoutItemPicture` vinculada al mapa (`arrows/NorthArrow_02.svg`) posicionada en la esquina superior derecha.

### 2.5. Dualidad de Ejecución (GUI & Headless CLI)
- **Modo Interactivo (QGIS GUI):** Si se ejecuta desde la Consola Python de QGIS (`iface` disponible), adopta automáticamente la extensión del canvas en pantalla (`iface.mapCanvas().extent()`), guarda el proyecto y abre el **Diseñador de Composiciones** (`iface.openLayoutDesigner`).
- **Modo Autónomo (Standalone / OSGeo4W):** Si se ejecuta mediante `python-qgis-ltr.bat`, inicializa `QgsApplication`, carga el proyecto `.qgz`, encuadra automáticamente sobre la máscara urbana `Mask_Nucleo_SantaCruz` y exporta los archivos sin requerir interfaz gráfica.

---

## 3. Entregables Generados

| Recurso | Ruta | Descripción |
| :--- | :--- | :--- |
| **Script PyQGIS** | [`qgis_create_grouped_legend_layout.py`](file:///c:/dev/QGIS-testing/QGIS_scripts/qgis_create_grouped_legend_layout.py) | Generador completo del layout A4 con leyendas agrupadas. |
| **Plano PDF (Vector)** | [`Plano_Clasificacion_Suelo_A4.pdf`](file:///c:/dev/QGIS-testing/output/Plano_Clasificacion_Suelo_A4.pdf) | Exportación vectorial de alta definición (300 DPI). |
| **Plano PNG (Raster)** | [`Plano_Clasificacion_Suelo_A4.png`](file:///c:/dev/QGIS-testing/output/Plano_Clasificacion_Suelo_A4.png) | Render rasterizado a 150 DPI para previsualización inmediata. |

---

## 4. Guía de Ejecución Rápida

### En QGIS Desktop
1. Abrir la consola Python (`Ctrl + Alt + P`).
2. Abrir y ejecutar [`qgis_create_grouped_legend_layout.py`](file:///c:/dev/QGIS-testing/QGIS_scripts/qgis_create_grouped_legend_layout.py).
3. Se abrirá automáticamente la ventana del Diseñador de Composiciones con el plano listo para imprimir o ajustar.

### En Terminal / Batch
```powershell
C:\OSGeo4W\bin\python-qgis-ltr.bat c:\dev\QGIS-testing\QGIS_scripts\qgis_create_grouped_legend_layout.py
```
