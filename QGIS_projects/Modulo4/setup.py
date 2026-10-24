from qgis.core import QgsProject, QgsPrintLayout, QgsLayoutItemPage
from qgis.utils import iface

project = QgsProject.instance()

# 1. Remove the unnecessary raster layer (As per PDF page 2)
layer_to_remove = project.mapLayersByName("Categoría y subcategoría del suelo")
if layer_to_remove:
    project.removeMapLayer(layer_to_remove[0])
    print("[CLEANUP] Removed 'Categoría y subcategoría del suelo'.")

# 2. Create the required Print Layout (As per PDF Step 2)
layout_name = "Espacios Naturales Protegidos"
manager = project.layoutManager()

# Clear it if you already ran this script once
existing_layout = manager.layoutByName(layout_name)
if existing_layout:
    manager.removeLayout(existing_layout)

layout = QgsPrintLayout(project)
layout.initializeDefaults() # Creates the default blank page
layout.setName(layout_name)

# 3. Configure the page to A4 Horizontal (Landscape)
page_collection = layout.pageCollection()
page = page_collection.page(0)
page.setPageSize('A4', QgsLayoutItemPage.Landscape)

# Add it to the project
manager.addLayout(layout)
print(f"[SUCCESS] Layout '{layout_name}' created with A4 Horizontal settings.")

# 4. Magically open the Print Layout window so you can see it!
iface.openLayoutDesigner(layout)