"""
Restrict project and background layers to Santa Cruz de Tenerife (PROVMUN=38038 / layer AMB).

Performs:
1. Filters 'gobcan_unidades-estadisticas_nucleos' to only Santa Cruz (PROVMUN = '38038').
2. Creates an Inverted Polygon Mask ('Mask_SantaCruz') directly above the 'Background' group
   so all background imagery is clipped to the municipal boundary.
3. Sets default project view extent to Santa Cruz de Tenerife.
"""

import os
from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsInvertedPolygonRenderer,
    QgsSingleSymbolRenderer,
    QgsFillSymbol,
)
from qgis.utils import iface

project = QgsProject.instance()

# 1. Filter gobcan_unidades-estadisticas_nucleos
nucleos_layer = None
for lyr in project.mapLayers().values():
    if "unidades-estadisticas_nucleos" in lyr.name() or "gobcan_unidades" in lyr.name():
        nucleos_layer = lyr
        break

if nucleos_layer:
    # Filter by PROVMUN 38038 (Santa Cruz de Tenerife)
    nucleos_layer.setSubsetString('"PROVMUN" = \'38038\'')
    nucleos_layer.triggerRepaint()
    print(f"[+] 'gobcan_unidades-estadisticas_nucleos' filtered: {nucleos_layer.featureCount()} features in Santa Cruz.")
else:
    print("[-] Layer 'gobcan_unidades-estadisticas_nucleos' not found.")

# 2. Locate layer AMB (Santa Cruz municipal boundary)
amb_layer = None
for lyr in project.mapLayers().values():
    if lyr.name() == "AMB":
        amb_layer = lyr
        break

if not amb_layer:
    raise RuntimeError("Layer 'AMB' not found in project.")

# 3. Create or update Inverted Polygon Mask above the Background group
mask_name = "Mask_SantaCruz"
mask_layer = None
for lyr in project.mapLayers().values():
    if lyr.name() == mask_name:
        mask_layer = lyr
        break

if not mask_layer:
    mask_layer = QgsVectorLayer("Polygon?crs=" + amb_layer.crs().authid(), mask_name, "memory")
    dp = mask_layer.dataProvider()
    for feat in amb_layer.getFeatures():
        dp.addFeature(feat)
    project.addMapLayer(mask_layer, False)

    # Position right above Background group
    root = project.layerTreeRoot()
    bg_group = root.findGroup("Background")
    if bg_group:
        idx = root.children().index(bg_group)
        root.insertLayer(idx, mask_layer)
    else:
        root.addLayer(mask_layer)

# Solid white fill outside Santa Cruz
sym = QgsFillSymbol.createSimple({"color": "255,255,255,255", "outline_color": "no"})
inv_renderer = QgsInvertedPolygonRenderer(QgsSingleSymbolRenderer(sym))
mask_layer.setRenderer(inv_renderer)
mask_layer.triggerRepaint()
print(f"[+] '{mask_name}' active: Background clipped to Santa Cruz municipal boundary.")

# 4. Set project view extent to AMB
amb_extent = amb_layer.extent()
project.viewSettings().setDefaultViewExtent(amb_extent)
project.viewSettings().setPresetFullExtent(amb_extent)

if iface:
    iface.mapCanvas().setExtent(amb_extent)
    iface.mapCanvas().refresh()
    iface.layerTreeView().refreshLayerSymbology(mask_layer.id())

print("[SUCCESS] Project and Background restricted to Santa Cruz de Tenerife.")
