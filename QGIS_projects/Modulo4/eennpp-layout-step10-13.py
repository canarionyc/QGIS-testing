from qgis.core import (QgsProject, QgsLayoutItemAttributeTable, QgsLayoutItemPicture, 
                       QgsLayoutItemLabel, QgsLayoutPoint, QgsLayoutSize, QgsUnitTypes, 
                       QgsLayoutItemMap, QgsLayoutFrame)
from PyQt5.QtGui import QFont

# --- CONFIGURATION ---
LAYER_NAME = "eennpp" 
# ---------------------

project = QgsProject.instance()
layout = project.layoutManager().layoutByName("Espacios Naturales Protegidos")

if not layout:
    print("[ERROR] Layout not found.")
else:
    # Get the map and the layer
    map_item = next((item for item in layout.items() if isinstance(item, QgsLayoutItemMap)), None)
    eennpp_layer = project.mapLayersByName(LAYER_NAME)
    
    if not map_item:
        print("[ERROR] Could not find the Map item in the layout.")
    elif not eennpp_layer:
        print(f"[ERROR] Could not find a layer named '{LAYER_NAME}'.")
    else:
        eennpp_layer = eennpp_layer[0]

        # 1. THE TITLE (Paso 12)
        title = QgsLayoutItemLabel(layout)
        title.setText("Espacios Naturales Protegidos")
        title.setFont(QFont("Arial", 22, QFont.Bold))
        layout.addLayoutItem(title)
        title.attemptMove(QgsLayoutPoint(10, 5, QgsUnitTypes.LayoutMillimeters))
        title.attemptResize(QgsLayoutSize(120, 15, QgsUnitTypes.LayoutMillimeters))
        
        # 2. THE IMAGE / LOGO (Paso 11)
        logo = QgsLayoutItemPicture(layout)
        logo.setPicturePath(r"C:\dev\QGIS-testing\Modulo4\IDECanarias.jpg") 
        layout.addLayoutItem(logo)
        logo.attemptMove(QgsLayoutPoint(240, 5, QgsUnitTypes.LayoutMillimeters))
        logo.attemptResize(QgsLayoutSize(40, 15, QgsUnitTypes.LayoutMillimeters))

        # 3. THE ATTRIBUTE TABLE (Paso 10) - FIXED FOR MULTIFRAME
        table = QgsLayoutItemAttributeTable(layout)
        table.setVectorLayer(eennpp_layer)
        table.setDisplayOnlyVisibleFeatures(True) # Show only features visible in map
        table.setMaximumNumberOfFeatures(34)      # Max rows = 34
        
        # Add the MultiFrame logic
        layout.addMultiFrame(table)
        
        # Create a physical frame to display the table on the page
        frame = QgsLayoutFrame(layout, table)
        frame.attemptMove(QgsLayoutPoint(10, 130, QgsUnitTypes.LayoutMillimeters))
        frame.attemptResize(QgsLayoutSize(80, 60, QgsUnitTypes.LayoutMillimeters))
        
        # Connect the frame to the table and add the frame to the layout
        table.addFrame(frame)
        layout.addLayoutItem(frame)

        # 4. THE ATLAS CONFIGURATION (Paso 13)
        atlas = layout.atlas()
        atlas.setEnabled(True)
        atlas.setCoverageLayer(eennpp_layer)
        atlas.setPageNameExpression('"nombre"')
        
        # Link map to atlas
        map_item.setAtlasDriven(True)
        map_item.setAtlasScalingMode(QgsLayoutItemMap.Auto)

        layout.refresh()
        print("[SUCCESS] Title, Logo, Table, and Atlas successfully added!")