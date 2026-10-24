print("--- QGIS LAYER DUMP ---")
for layer in QgsProject.instance().mapLayers().values():
    print(layer.name())
print("-----------------------")