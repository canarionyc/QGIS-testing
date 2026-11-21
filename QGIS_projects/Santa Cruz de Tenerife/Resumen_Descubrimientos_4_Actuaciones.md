# Resumen de Descubrimientos: Diagnóstico Territorial y Auditoría de las 4 Actuaciones de Planeamiento en Santa Cruz de Tenerife

**Autor:** Tomás González Llarena  
**Fecha:** Noviembre de 2026  
**Ámbito de estudio:** Término Municipal de Santa Cruz de Tenerife  
**Metodología:** Cruce de base de datos espacial normalizada FIP 2.0 en PostGIS ([Santa Cruz de Tenerife.qgz](file:///c:/dev/QGIS-testing/QGIS_projects/Santa%20Cruz%20de%20Tenerife/Santa%20Cruz%20de%20Tenerife.qgz)), series demográficas y migratorias del INE e ISTAC (2000-2025), y verificación aerofotogramétrica ortorrectificada de máxima actualidad de IDECanarias / GRAFCAN (OrtoExpress Urbana, 10-12,5 cm/píxel).

### Documentos Principales del Proyecto:
* **Informe Completo en Español (PDF):** [Master_ES.pdf](file:///c:/dev/QGIS-testing/QGIS_projects/Santa%20Cruz%20de%20Tenerife/Master_ES.pdf) ([Master_ES.tex](file:///c:/dev/QGIS-testing/QGIS_projects/Santa%20Cruz%20de%20Tenerife/Master_ES.tex))
* **Full Technical Report in English (PDF):** [Master_EN.pdf](file:///c:/dev/QGIS-testing/QGIS_projects/Santa%20Cruz%20de%20Tenerife/Master_EN.pdf) ([Master_EN.tex](file:///c:/dev/QGIS-testing/QGIS_projects/Santa%20Cruz%20de%20Tenerife/Master_EN.tex))
* **LinkedIn Visual Carousel (PDF):** [LinkedIn_Carousel_EN.pdf](file:///c:/dev/QGIS-testing/QGIS_projects/Santa%20Cruz%20de%20Tenerife/LinkedIn_Carousel_EN.pdf) ([LinkedIn_Carousel_EN.tex](file:///c:/dev/QGIS-testing/QGIS_projects/Santa%20Cruz%20de%20Tenerife/LinkedIn_Carousel_EN.tex))

---

## 1. Contexto General y Estructura de Gestión del Suelo

A partir del análisis de la base de datos oficial del Plan General de Ordenación (PGO de Santa Cruz de Tenerife, formato FIP 2.0; ver [10_resumen_ejecutivo_ES.tex](file:///c:/dev/QGIS-testing/QGIS_projects/Santa%20Cruz%20de%20Tenerife/sections/10_resumen_ejecutivo_ES.tex)) y su confrontación con la situación jurídica y territorial actual, se revelan los siguientes parámetros estructurales:

1. **Hiperconcentración en Suelo Urbano No Consolidado (SUNC):**
   - De las 128 Unidades de Actuación (UAs) delimitadas en todo el término municipal, el **97,7% (125 UAs)** corresponden a Suelo Urbano No Consolidado (SUNC).
   - Estas 125 unidades acumulan **1.557.793 m²c de edificabilidad lucrativa** y una superficie bruta de **2.915.364 m²** (consultar datos tabulados en [table_land_classes.tex](file:///c:/dev/QGIS-testing/QGIS_projects/Santa%20Cruz%20de%20Tenerife/tables/table_land_classes.tex) y visualización en [chart_land_classes.pdf](file:///c:/dev/QGIS-testing/QGIS_projects/Santa%20Cruz%20de%20Tenerife/figures/chart_land_classes.pdf)).
   - Por el contrario, el Suelo Urbanizable Sectorizado (SUS) se reduce a solo **3 unidades** (ubicadas en El Tablero), con **80.778 m²c** y 112.021 m² de suelo.

2. **Dominio de la Gestión Privada por Compensación:**
   - El **58,6%** de la edificabilidad lucrativa (75 UAs, más de 1,16 millones de m²c) estaba encomendado al sistema de **Compensación privada** (ver [table_execution_systems.tex](file:///c:/dev/QGIS-testing/QGIS_projects/Santa%20Cruz%20de%20Tenerife/tables/table_execution_systems.tex)). En este régimen, los propietarios deben organizarse en Juntas de Compensación, asumir los costes de urbanización y ceder el suelo dotacional y los aprovechamientos públicos (Título V de la Ley del Suelo de Canarias; [BOE-A-2017-10295-consolidado.pdf](file:///c:/dev/QGIS-testing/QGIS_projects/Santa%20Cruz%20de%20Tenerife/supporting_docs/BOE-A-2017-10295-consolidado.pdf)).
   - El sistema de **Cooperación pública** abarca el **35,2%** (45 UAs, 463.292 m²c), donde la ejecución material corresponde al Ayuntamiento a repercutir sobre los propietarios.
   - Expropiación, convenios urbanísticos o sistemas no especificados concentran el 6,2% restante.

3. **Vencimiento del Horizonte Temporal Legal:**
   - La programación del PGO preveía plazos máximos de gestión y ejecución: 12 meses para la iniciativa privada/reparcelación (113 UAs), 24 meses para proyectos de urbanización (104 UAs), 48 meses para el primer cuatrienio (93 UAs) y un horizonte tope de 96 meses (8 años, 2015-2023).
   - Todos los plazos legales vencieron en 2023 sin que las unidades se materializaran.

---

## 2. El Descubrimiento Central: El Gran Embudo Normativo y Material

La contrastación aerofotogramétrica y documental (ver [15_introduccion_ES.tex](file:///c:/dev/QGIS-testing/QGIS_projects/Santa%20Cruz%20de%20Tenerife/sections/15_introduccion_ES.tex) y [40_conclusiones_ES.tex](file:///c:/dev/QGIS-testing/QGIS_projects/Santa%20Cruz%20de%20Tenerife/sections/40_conclusiones_ES.tex)) desmonta los relatos convencionales sobre el territorio de la capital:

* **La falacia del "sobreturismo habitacional":** La percepción ciudadana de saturación en el casco responde al paso de más de 900.000 cruceristas anuales (más de 600.000 transeúntes de escala de 4 a 8 horas) que duermen en los barcos y consumen espacio público pero **cero plazas residenciales**. El alojamiento turístico reglado en hoteles y apartamentos apenas alcanza unas 1.600 plazas equivalentes (menos del 0,8% del censo municipal; consultar gráfico [demographics_trend.pdf](file:///c:/dev/QGIS-testing/QGIS_projects/Santa%20Cruz%20de%20Tenerife/figures/demographics_trend.pdf) y script [plot_demographics.py](file:///c:/dev/QGIS-testing/QGIS_projects/Santa%20Cruz%20de%20Tenerife/plot_demographics.py)).
* **La paradoja de la densidad:** La cifra promedio municipal de 1.385 hab/km² es una ilusión aritmética porque el 80% del municipio es el Parque Rural de Anaga (Reserva de la Biosfera), abrupto y protegido por ley contra todo desarrollo urbano (ver plano oficial [pgo_sctf_po02_2.jpg](file:///c:/dev/QGIS-testing/QGIS_projects/Santa%20Cruz%20de%20Tenerife/premade_maps/pgo_sctf_po02_2.jpg)). En la huella urbana real donde vive la población, la densidad supera los 12.000 hab/km², equiparable a los ensanches de Madrid o Barcelona.
* **El verdadero origen de la crisis:** La escasez de vivienda y el alza de precios obedecen a un **bloqueo interno de la oferta de suelo**. Por un lado, la anulación judicial del PGO 2013/2015 (Sentencia TSJC 116/2014) y la suspensión de la Ordenanza Provisional de 2022 (Sentencia TSJC 70/2023; ver [50_bibliografia_ES.tex](file:///c:/dev/QGIS-testing/QGIS_projects/Santa%20Cruz%20de%20Tenerife/sections/50_bibliografia_ES.tex)) devolvieron a la ciudad al obsoleto PGOU de 2005 en un régimen de inseguridad jurídica total. Por otro lado, la atomización de la propiedad en SUNC hizo inviables las juntas de compensación. Al vencer los plazos en 2023, el Ayuntamiento carecía de capacidad técnica y financiera para sustituir el sistema e intervenir de oficio, dejando el suelo congelado.

---

## 3. Diagnóstico Detallado de las 4 Actuaciones Auditadas

Al superponer en SIG ([Santa Cruz de Tenerife.qgz](file:///c:/dev/QGIS-testing/QGIS_projects/Santa%20Cruz%20de%20Tenerife/Santa%20Cruz%20de%20Tenerife.qgz)) las poligonales de las Unidades de Actuación (`v_unidades_actuacion`) con la ortofoto aérea de máxima resolución de IDECanarias/GRAFCAN (2024-2025; ver [20_diagnostico_fip_ES.tex](file:///c:/dev/QGIS-testing/QGIS_projects/Santa%20Cruz%20de%20Tenerife/sections/20_diagnostico_fip_ES.tex)), se constata de manera empírica la inejecución de los cuatro grandes nodos de transformación urbana del municipio:

### Actuación 1: Suelo Urbanizable Sectorizado — El Tablero (Sector SUS 5.13 y Ámbito 5.16.2)
* **Unidades comprendidas:** UA-1, UA-2 y UA-3 del sector SSU 5.13, junto a la contigua UA-RT-1 del Ámbito 5.16.2.
* **Importancia estratégica:** Concentra la totalidad del suelo urbanizable residencial sectorizado de Santa Cruz de Tenerife, con más de 80.000 m²c de edificabilidad lucrativa programada para responder al crecimiento metropolitano.
* **Documentación urbanística:** Cédula y consulta oficial de planeamiento en [SUSO-ejemplo.pdf](file:///c:/dev/QGIS-testing/QGIS_projects/Santa%20Cruz%20de%20Tenerife/Consulta%20de%20Planeamiento/SUSO-ejemplo.pdf).
* **Diagnóstico sobre el terreno (Ortofoto reciente):**
  - Ortofoto de verificación: [orto_detalle_el_tablero.jpg](file:///c:/dev/QGIS-testing/QGIS_projects/Santa%20Cruz%20de%20Tenerife/figures/orto_detalle_el_tablero.jpg) (alta resolución: [orto_detalle_el_tablero.png](file:///c:/dev/QGIS-testing/QGIS_projects/Santa%20Cruz%20de%20Tenerife/figures/orto_detalle_el_tablero.png)).
  - La totalidad del sector se mantiene como una gran explanada terrosa y baldía encajada entre el casco consolidado de El Tablero y las instalaciones del campo de fútbol.
  - No se ha ejecutado la red viaria estructurante interior ni las conexiones viarias planificadas (a excepción parcial de la UA-1).
  - No existen aceras recepcionadas, servicios urbanos enterrados ni se ha levantado una sola de las viviendas previstas.
  - Diez años después de la previsión de desarrollo, el único suelo urbanizable de expansión residencial de la capital permanece en estado rústico improductivo.

### Actuación 2: Suelo Urbano No Consolidado — Cabo Llanos (Ámbito 2.5.3)
* **Unidad comprendida:** UA-RT-1 del Ámbito 2.5.3.
* **Importancia estratégica:** Dispone de una capacidad lucrativa superior a los 25.000 m²c ubicada en el nodo terciario, comercial y residencial de mayor cotización de Santa Cruz de Tenerife (frente marítimo de expansión sur, junto a las Torres de Santa Cruz y el intercambiador).
* **Documentación urbanística:** Cédula y consulta oficial de planeamiento en [SUNC-ejemplo.pdf](file:///c:/dev/QGIS-testing/QGIS_projects/Santa%20Cruz%20de%20Tenerife/Consulta%20de%20Planeamiento/SUNC-ejemplo.pdf).
* **Diagnóstico sobre el terreno (Ortofoto reciente):**
  - Ortofoto de verificación: [orto_detalle_cabo_llanos.jpg](file:///c:/dev/QGIS-testing/QGIS_projects/Santa%20Cruz%20de%20Tenerife/figures/orto_detalle_cabo_llanos.jpg) (alta resolución: [orto_detalle_cabo_llanos.png](file:///c:/dev/QGIS-testing/QGIS_projects/Santa%20Cruz%20de%20Tenerife/figures/orto_detalle_cabo_llanos.png)).
  - El polígono delimitado representa un **vacío urbano absoluto**: un solar de tierra y polvo completamente encajado entre manzanas residenciales modernas de alta densidad completamente colmatadas.
  - El espacio se utiliza de manera informal como descampado y aparcamiento precario sobre tierra.
  - No se ha completado el proyecto de reparcelación, ni la cesión de aprovechamientos públicos, ni las obras de urbanización y viales perimetrales, perpetuando una brecha en la trama urbana más cotizada de la capital.

### Actuación 3: Suelo Urbano No Consolidado — Barranco de Santos (La Ladera)
* **Unidades comprendidas:** Ámbitos 1.7.4A1 (La Ladera A1) y 1.7.4A2 (La Ladera A2).
* **Importancia estratégica:** Operación de sutura urbana y regeneración ambiental del frente urbano que asoma sobre el cauce del Barranco de Santos, elemento vertebrador de la orografía de la ciudad.
* **Documentación urbanística y levantamiento de campo:** Reporte fotográfico geolocalizado con flechas directrices en [Plano_Fotografias.pdf](file:///c:/dev/QGIS-testing/QGIS_projects/Santa%20Cruz%20de%20Tenerife/Plano_Fotografias.pdf).
* **Diagnóstico sobre el terreno (Ortofoto reciente):**
  - Ortofoto de verificación: [orto_detalle_barranco_santos.jpg](file:///c:/dev/QGIS-testing/QGIS_projects/Santa%20Cruz%20de%20Tenerife/figures/orto_detalle_barranco_santos.jpg) (alta resolución: [orto_detalle_barranco_santos.png](file:///c:/dev/QGIS-testing/QGIS_projects/Santa%20Cruz%20de%20Tenerife/figures/orto_detalle_barranco_santos.png)).
  - **Ámbito 1.7.4A1 (La Ladera A1):** Permanece como un mosaico degradado de autoconstrucción irregular preexistente y una explanada de tierra sin pavimentar utilizada como estacionamiento no regulado.
  - **Ámbito 1.7.4A2 (La Ladera A2):** Se mantiene como una ladera escarpada de fuerte pendiente cubierta de matorral seco que vierte directamente al cauce del barranco, carente de viales, encintado de aceras, redes de saneamiento o alumbrado público.
  - La falta de ejecución impide consolidar el parque lineal del barranco y regularizar los accesos peatonales y rodados del barrio.

### Actuación 4: Suelo Urbano No Consolidado — Montaña de Taco
* **Unidades comprendidas:** Ámbitos 4.9.4 (Parque Montaña de Taco), 4.9.5 (Montaña de Taco Residencial) y 4.9.3 (Montaña de Taco Industrial).
* **Importancia estratégica:** Nodo limítrofe metropolitano entre los términos de Santa Cruz de Tenerife y San Cristóbal de La Laguna, con una triple vocación complementaria (parque urbano estructurante, tejido residencial y modernización industrial).
* **Diagnóstico sobre el terreno (Ortofoto reciente):**
  - Ortofoto de verificación: [orto_detalle_montana_taco.jpg](file:///c:/dev/QGIS-testing/QGIS_projects/Santa%20Cruz%20de%20Tenerife/figures/orto_detalle_montana_taco.jpg) (alta resolución: [orto_detalle_montana_taco.png](file:///c:/dev/QGIS-testing/QGIS_projects/Santa%20Cruz%20de%20Tenerife/figures/orto_detalle_montana_taco.png)).
  - **Ámbito 4.9.4 (Parque Urbano):** Continúa presentándose como una inmensa cantera extractiva de áridos a cielo abierto, sin que se hayan iniciado las tareas de restauración topográfica, revegetación o adecuación como sistema general de parque metropolitano.
  - **Ámbito 4.9.5 (Residencial):** Permanece como una ladera terrosa baldía sin traza viaria ni proyectos de edificación iniciados.
  - **Ámbito 4.9.3 (Industrial):** Conserva naves industriales obsoletas de tipología preconstitucional y patios de acopio de maquinaria y chatarra, sin haber llevado a cabo la reconversión y saneamiento urbanístico ordenado por el planeamiento.

---

## 4. Síntesis y Conclusiones Territoriales

1. **Parálisis Sistémica de la Oferta:**
   La evidencia aerofotogramétrica demuestra que la inejecución de los plazos temporales (vencidos en 2023) no fue un retraso puntual, sino una parálisis estructural. Los 1,55 millones de m²c de suelo lucrativo previstos siguen secuestrados por la anulación judicial del marco normativo y la inviabilidad práctica del sistema de compensación en un tejido urbano atomizado.

2. **Divergencia entre Dinámica Demográfica y Rigidez del Suelo:**
   A pesar de que el censo global parece plano (+2% en 15 años), la presión habitacional se ha disparado por dos factores verificados en las estadísticas oficiales:
   - **La inversión del flujo migratorio con América:** Desde 2016 el municipio registra un saldo neto positivo continuo de más de 2.000 residentes permanentes al año (+2.618 en 2023; ver gráfico [migration_trend.pdf](file:///c:/dev/QGIS-testing/QGIS_projects/Santa%20Cruz%20de%20Tenerife/figures/migration_trend.pdf), serie [migration_sctf.json](file:///c:/dev/QGIS-testing/QGIS_projects/Santa%20Cruz%20de%20Tenerife/migration_sctf.json) y script [plot_migration.py](file:///c:/dev/QGIS-testing/QGIS_projects/Santa%20Cruz%20de%20Tenerife/plot_migration.py)), con un censo extranjero cuadruplicado (de 4.473 en el año 2000 a 16.776 en 2025), además de retornados con nacionalidad por descendencia que demandan vivienda de larga estancia.
   - **La reducción del tamaño medio del hogar:** De 3,4 personas por hogar en los años sesenta a 2,2 en la actualidad (consultar series de renta en [income_trend.pdf](file:///c:/dev/QGIS-testing/QGIS_projects/Santa%20Cruz%20de%20Tenerife/figures/income_trend.pdf) y script [plot_income.py](file:///c:/dev/QGIS-testing/QGIS_projects/Santa%20Cruz%20de%20Tenerife/plot_income.py)), lo que genera un déficit matemático de más de 34.000 viviendas adicionales para alojar al mismo volumen de población.

3. **Impacto Metropolitano:**
   Al ser materialmente imposible edificar nuevas viviendas con estándares modernos (especialmente con plazas de garaje que absorban la altísima tasa de motorización insular de 830 vehículos/1.000 hab), la demanda solvente es expulsada hacia municipios vecinos (La Laguna, El Rosario, Candelaria), retroalimentando el colapso viario diario de las autopistas TF-5 y TF-1.

4. **Cartografía Oficial del Plan de Etapas y Ordenación:**
   Consultar los planos apaisados completos integrados en el anexo ([60_anexo_ES.tex](file:///c:/dev/QGIS-testing/QGIS_projects/Santa%20Cruz%20de%20Tenerife/sections/60_anexo_ES.tex)):
   - Modelo Estructural PO-01: [pgo_sctf_po01_1.jpg](file:///c:/dev/QGIS-testing/QGIS_projects/Santa%20Cruz%20de%20Tenerife/premade_maps/pgo_sctf_po01_1.jpg)
   - Clasificación del Suelo PO-02: [pgo_sctf_po02_2.jpg](file:///c:/dev/QGIS-testing/QGIS_projects/Santa%20Cruz%20de%20Tenerife/premade_maps/pgo_sctf_po02_2.jpg)
   - Ámbitos de Gestión y Sectores PO-03: [pgo_sctf_po03.jpg](file:///c:/dev/QGIS-testing/QGIS_projects/Santa%20Cruz%20de%20Tenerife/premade_maps/pgo_sctf_po03.jpg)
   - Usos Globales Característicos PO-04: [pgo_sctf_po04.jpg](file:///c:/dev/QGIS-testing/QGIS_projects/Santa%20Cruz%20de%20Tenerife/premade_maps/pgo_sctf_po04.jpg)

---
*Documento compilado a partir de los trabajos de investigación espacial y planeamiento del proyecto QGIS-testing (Santa Cruz de Tenerife).*
