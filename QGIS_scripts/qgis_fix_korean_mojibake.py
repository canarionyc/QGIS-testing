from qgis.core import QgsProject
from qgis.utils import iface

active_layer = iface.activeLayer()
root = QgsProject.instance().layerTreeRoot()
model = iface.layerTreeView().layerTreeModel()

if active_layer:
    layer_node = root.findLayer(active_layer.id())
    legend_nodes = model.layerLegendNodes(layer_node)
    
    print("--- INICIO DEL DIAGNÓSTICO ---")
    # Analizamos solo las 3 primeras categorías
    for node in legend_nodes[:3]: 
        text = node.data(0)
        if text:
            print(f"Texto visible: {text}")
            print(f"Representación cruda: {repr(text)}")
            print(f"Bytes UTF-8: {text.encode('utf-8', errors='replace')}")
            print("-" * 30)
    print("--- FIN DEL DIAGNÓSTICO ---")
else:
    print("Selecciona la capa primero.")