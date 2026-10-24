from qgis.core import (QgsProject, QgsLayoutItemMap, QgsLayoutSize, 
                       QgsLayoutPoint, QgsRectangle, QgsUnitTypes, 
                       QgsLayoutItemMapGrid)

# 1. Conectar con el proyecto y el diseño que creamos antes
project = QgsProject.instance()
layout = project.layoutManager().layoutByName("Espacios Naturales Protegidos")

if not layout:
    print("[ERROR] No se encontró el diseño de impresión. ¿Ejecutaste el script anterior?")
else:
    # 2. Crear el elemento de Mapa y añadirlo a la página
    map_item = QgsLayoutItemMap(layout)
    layout.addLayoutItem(map_item)

    # 3. Tamaño y posición (Dejando un pequeño margen en el A4 de 297x210 mm)
    # Lo colocamos a 10mm del borde y le damos un tamaño de 277x190mm
    map_item.attemptMove(QgsLayoutPoint(10, 10, QgsUnitTypes.LayoutMillimeters))
    map_item.attemptResize(QgsLayoutSize(277, 190, QgsUnitTypes.LayoutMillimeters))

    # 4. Configurar el encuadre (Centro de Gran Canaria) y la escala
    # Coordenadas aproximadas del centro de Gran Canaria en UTM 28N (EPSG:32628)
    center_x = 445000
    center_y = 3088000
    
    # Creamos un rectángulo inicial y se lo pasamos al mapa
    rect = QgsRectangle(center_x - 10000, center_y - 10000, center_x + 10000, center_y + 10000)
    map_item.setExtent(rect)
    
    # Forzamos la escala exacta que pide el tutorial
    map_item.setScale(250000)

    # 5. Añadir y configurar la cuadrícula (Grid)
    grid = QgsLayoutItemMapGrid("Cuadrícula 1", map_item)
    grid.setEnabled(True)
    grid.setIntervalX(10000)  # Línea vertical cada 10 km (10.000 metros)
    grid.setIntervalY(10000)  # Línea horizontal cada 10 km
    
    # Mostrar las coordenadas en los bordes del mapa
    grid.setAnnotationEnabled(True)
    
    # Añadimos la cuadrícula al mapa
    map_item.grids().addGrid(grid)

    # 6. Poner un borde negro simple alrededor del mapa
    map_item.setFrameEnabled(True)

    print("[ÉXITO] Mapa centrado a escala 1:250.000 y cuadrícula generados correctamente.")