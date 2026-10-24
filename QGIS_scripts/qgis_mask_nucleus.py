"""
Create an Inverted Polygon Mask layer for the filtered population nucleus
in 'gobcan_unidades-estadisticas_nucleos' (e.g. FPMCUN = '20010101380380025201').
"""

from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsFeature,
    QgsInvertedPolygonRenderer,
    QgsSingleSymbolRenderer,
    QgsFillSymbol,
)
from qgis.utils import iface

project = QgsProject.instance()

# 1. Locate nucleos layer
nucleos = None
for lyr in project.mapLayers().values():
    if "unidades-estadisticas_nucleos" in lyr.name() or "gobcan_unidades" in lyr.name():
        nucleos = lyr
        break

if not nucleos:
    raise RuntimeError("Layer 'gobcan_unidades-estadisticas_nucleos' not found.")

if nucleos.featureCount() == 0:
    raise RuntimeError("No features found in 'gobcan_unidades-estadisticas_nucleos'. Check filter.")

feat = next(nucleos.getFeatures())
nucleus_name = feat.get("NNUC") or "Nucleo"
fpmcun = feat.get("FPMCUN") or ""
print(f"Target Nucleus: {nucleus_name} (FPMCUN: {fpmcun})")

# 2. Re-create or update Mask_Nucleo_SantaCruz
mask_name = "Mask_Nucleo_SantaCruz"
old_mask = None
for lyr in project.mapLayers().values():
    if lyr.name() == mask_name:
        old_mask = lyr
        break

if old_mask:
    project.removeMapLayer(old_mask.id())

# Create memory layer with polygon geometry from the nucleus feature
mask_layer = QgsVectorLayer("MultiPolygon?crs=" + nucleos.crs().authid(), mask_name, "memory")
dp = mask_layer.dataProvider()
f = QgsFeature()
f.setGeometry(feat.geometry())
dp.addFeature(f)
mask_layer.updateExtents()

# 3. Apply Inverted Polygon Renderer (solid white outside the nucleus)
sym = QgsFillSymbol.createSimple({"color": "255,255,255,255", "outline_color": "no"})
inv_renderer = QgsInvertedPolygonRenderer(QgsSingleSymbolRenderer(sym))
mask_layer.setRenderer(inv_renderer)

# 4. Insert into the layer tree right above PGOU group (so it masks both PGOU and Background)
project.addMapLayer(mask_layer, False)
root = project.layerTreeRoot()
pgou_group = root.findGroup("PGOU")
if pgou_group:
    idx = root.children().index(pgou_group)
    root.insertLayer(idx, mask_layer)
else:
    root.insertLayer(1, mask_layer)

mask_layer.triggerRepaint()

# 5. Zoom map canvas to the nucleus bounding box with 5% margin
bbox = feat.geometry().boundingBox()
bbox.grow(bbox.width() * 0.05)
if iface:
    iface.mapCanvas().setExtent(bbox)
    iface.mapCanvas().refresh()
    iface.layerTreeView().refreshLayerSymbology(mask_layer.id())

print(f"[SUCCESS] '{mask_name}' created and zoomed to {nucleus_name}.")
