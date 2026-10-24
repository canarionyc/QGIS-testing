from qgis.core import QgsProject, QgsLayoutItemMap, QgsLayoutItemScaleBar, QgsLayoutItemPicture, QgsLayoutItemLegend
from PyQt5.QtGui import QColor

project = QgsProject.instance()
layout = project.layoutManager().layoutByName("Espacios Naturales Protegidos")

if not layout:
    print("[ERROR] Layout not found.")
else:
    for item in layout.items():
        # 1. The Map: Give it a nice, cartographic ocean blue
        if isinstance(item, QgsLayoutItemMap):
            item.setBackgroundEnabled(True)
            # A soft, classic ocean blue (RGB: 198, 226, 255)
            item.setBackgroundColor(QColor(198, 226, 255)) 
            item.setFrameEnabled(True) # Keep the black border around the whole map
            
        # 2. The Scale Bar: Make it transparent
        elif isinstance(item, QgsLayoutItemScaleBar):
            item.setBackgroundEnabled(False)
            item.setFrameEnabled(False) 
            
        # 3. The North Arrow: Make it transparent
        elif isinstance(item, QgsLayoutItemPicture):
            item.setBackgroundEnabled(False)
            item.setFrameEnabled(False)
            
        # 4. The Legend: Make it transparent
        elif isinstance(item, QgsLayoutItemLegend):
            item.setBackgroundEnabled(False)
            item.setFrameEnabled(False)
            
    # Force the layout window to redraw with the new settings
    layout.refresh()
    print("[SUCCESS] Ocean applied and backgrounds removed! Check your Layout Designer.")