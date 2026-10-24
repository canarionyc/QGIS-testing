from qgis.core import QgsProject, QgsMapLayerType, QgsWkbTypes

project = QgsProject.instance()

print("==== QGIS PROJECT STATE DUMP ====")
print(f"Project Path: {project.fileName() or 'Unsaved Project'}")
print(f"Project CRS: {project.crs().authid()}")

print("\n--- MAP LAYERS ---")
layers = project.mapLayers()
if not layers:
    print("  No layers currently loaded.")
else:
    for layer_id, layer in layers.items():
        if layer.type() == QgsMapLayerType.VectorLayer:
            geom_type = QgsWkbTypes.displayString(layer.wkbType())
            print(f"  [Vector] {layer.name()} | CRS: {layer.crs().authid()} | Geom: {geom_type} | Features: {layer.featureCount()}")
        elif layer.type() == QgsMapLayerType.RasterLayer:
            print(f"  [Raster] {layer.name()} | CRS: {layer.crs().authid()}")
        else:
            print(f"  [Other] {layer.name()}")

print("\n--- PRINT LAYOUTS (Diseñador de impresión) ---")
layouts = project.layoutManager().layouts()
if not layouts:
    print("  No print layouts found.")
else:
    for layout in layouts:
        print(f"  [Layout] Name: {layout.name()}")
        
print("=================================")