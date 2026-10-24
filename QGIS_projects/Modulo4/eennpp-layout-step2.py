from qgis.core import (QgsProject, QgsLayoutItemLegend, QgsLayoutItemScaleBar, 
                       QgsLayoutItemPicture, QgsLayoutPoint, QgsLayoutSize, 
                       QgsUnitTypes)
import os

project = QgsProject.instance()
layout = project.layoutManager().layoutByName("Espacios Naturales Protegidos")

if not layout:
    print("[ERROR] No se encontró el diseño. Abre el administrador de composiciones primero.")
else:
    # 1. Buscar el elemento de Mapa que creamos antes (lo necesitamos para vincular la escala)
    # Buscamos por el tipo de elemento (65639 es el ID interno para Mapas)
    map_item = next((item for item in layout.items() if item.type() == 65639), None)

    if not map_item:
        print("[ERROR] No se encontró el mapa en el diseño.")
    else:
        # --- 2. AÑADIR LA LEYENDA ---
        legend = QgsLayoutItemLegend(layout)
        legend.setTitle("Leyenda")
        layout.addLayoutItem(legend)
        # Colocarla en la esquina inferior izquierda (fuera del mapa o en un hueco)
        legend.attemptMove(QgsLayoutPoint(15, 120, QgsUnitTypes.LayoutMillimeters))
        print("[ÉXITO] Leyenda añadida.")

        # --- 3. AÑADIR LA BARRA DE ESCALA ---
        scalebar = QgsLayoutItemScaleBar(layout)
        scalebar.setStyle('Single Box') # Estilo de caja simple
        scalebar.setLinkedMap(map_item) # Vincularla a nuestro mapa de Gran Canaria
        scalebar.applyDefaultSize()
        layout.addLayoutItem(scalebar)
        # Colocarla en la esquina inferior derecha
        scalebar.attemptMove(QgsLayoutPoint(200, 180, QgsUnitTypes.LayoutMillimeters))
        print("[ÉXITO] Barra de escala añadida.")

        # --- 4. AÑADIR LA FLECHA DEL NORTE ---
        north_arrow = QgsLayoutItemPicture(layout)
        # Usamos una de las flechas SVG que vienen por defecto en QGIS
        # svg_path = os.path.join(QgsApplication.svgPaths()[0], "arrows", "NorthArrow_01.svg")
        svg_path = os.path.join( "arrows", "NorthArrow_01.svg")
        north_arrow.setPicturePath(svg_path)
        layout.addLayoutItem(north_arrow)
        north_arrow.attemptResize(QgsLayoutSize(15, 15, QgsUnitTypes.LayoutMillimeters))
        # Colocarla en la esquina superior derecha
        north_arrow.attemptMove(QgsLayoutPoint(260, 15, QgsUnitTypes.LayoutMillimeters))
        print("[ÉXITO] Flecha de Norte añadida.")

        # Refrescar la vista
        layout.refresh()
        print("[LISTO] Revisa tu Diseñador de Impresión.")