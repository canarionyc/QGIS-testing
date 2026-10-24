from qgis.core import QgsProject, QgsLayoutItemMap, QgsLayoutItemScaleBar, QgsLayoutItemPicture, QgsLayoutItemLegend
from PyQt5.QtGui import QColor

project = QgsProject.instance()
layout = project.layoutManager().layoutByName("Espacios Naturales Protegidos")

if not layout:
    print("[ERROR] Layout not found.")
else:
    for item in layout.items():
        # 1. Give the Map a light blue background to represent the ocean
        if isinstance(item, QgsLayoutItemMap):
            item.setBackgroundEnabled(True)
            # Alice Blue: a very subtle, professional water color
            item.setBackgroundColor(QColor(240, 248, 255)) 
            
        # 2. Give the Scale Bar a white background with a neat frame
        elif isinstance(item, QgsLayoutItemScaleBar):
            item.setBackgroundEnabled(True)
            item.setBackgroundColor(QColor("white"))
            item.setFrameEnabled(True) # Adds a black border
            
        # 3. Give the North Arrow a white background and frame
        elif isinstance(item, QgsLayoutItemPicture):
            item.setBackgroundEnabled(True)
            item.setBackgroundColor(QColor("white"))
            item.setFrameEnabled(True)
            
        # 4. Do the same for the Legend just in case it overlaps the island!
        elif isinstance(item, QgsLayoutItemLegend):
            item.setBackgroundEnabled(True)
            item.setBackgroundColor(QColor("white"))
            item.setFrameEnabled(True)
            
    # Tell QGIS to redraw the layout window
    layout.refresh()
    print("[SUCCESS] Visibility fixed! Check the Layout Designer.")