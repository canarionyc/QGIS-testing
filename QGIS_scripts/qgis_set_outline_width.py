"""
Batch update the outline (stroke) width for all rules/categories in layer CLA.
"""

from qgis.core import QgsProject
from qgis.utils import iface

# --- CONFIGURATION ---
LAYER_NAME = "CLA"
NEW_STROKE_WIDTH_MM = 0.28  # Width in millimeters (try 0.20 to 0.40 mm)
# ---------------------

project = QgsProject.instance()

# Find target layer
layer = None
for lyr in project.mapLayers().values():
    if lyr.name() == LAYER_NAME:
        layer = lyr
        break

if not layer:
    raise RuntimeError(f"Layer '{LAYER_NAME}' not found.")

def set_rule_stroke_width(rule, width):
    sym = rule.symbol()
    if sym:
        for sl in sym.symbolLayers():
            sl.setStrokeWidth(width)
    for child in rule.children():
        set_rule_stroke_width(child, width)

renderer = layer.renderer()

if renderer.type() == "RuleRenderer":
    set_rule_stroke_width(renderer.rootRule(), NEW_STROKE_WIDTH_MM)
elif renderer.type() == "categorizedSymbol":
    for cat in renderer.categories():
        if cat.symbol():
            for sl in cat.symbol().symbolLayers():
                sl.setStrokeWidth(NEW_STROKE_WIDTH_MM)
else:
    # Single symbol
    sym = renderer.symbol()
    if sym:
        for sl in sym.symbolLayers():
            sl.setStrokeWidth(NEW_STROKE_WIDTH_MM)

# Refresh layer rendering and UI
layer.triggerRepaint()
if iface:
    iface.layerTreeView().refreshLayerSymbology(layer.id())
    iface.mapCanvas().refresh()

print(f"[SUCCESS] Updated all '{LAYER_NAME}' outlines to {NEW_STROKE_WIDTH_MM} mm.")
