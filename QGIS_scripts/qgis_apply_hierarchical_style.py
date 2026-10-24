import os
import csv
from qgis.core import (
    QgsProject,
    QgsRuleBasedRenderer,
    QgsFillSymbol,
)
from qgis.utils import iface

# 1. Configuration
CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "color_ref.csv")
LAYER_NAME = "CLA"

# 2. Get the target layer
layer = None
for lyr in QgsProject.instance().mapLayers().values():
    if lyr.name() == LAYER_NAME:
        layer = lyr
        break

if not layer:
    raise RuntimeError(f"Layer '{LAYER_NAME}' not found in active QGIS project.")

# 3. Read categories from CSV and organize into groups
groups = {}
with open(CSV_PATH, mode="r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        group_name = row.get("GROUP", "General")
        if group_name not in groups:
            groups[group_name] = []
        groups[group_name].append({
            "code": row["ETIPLAN"],
            "label": f"{row['ETIPLAN']} - {row['TXTPLAN']}",
            "color": row["color_hex"],
            "outline": row.get("outline_hex", "#333333"),
            "opacity": float(row.get("opacity", 0.8)),
        })

# 4. Build hierarchical Rule-Based Renderer
root_rule = QgsRuleBasedRenderer.Rule(None)

for group_name, items in groups.items():
    group_rule = QgsRuleBasedRenderer.Rule(None, 0, 0, "", group_name)
    for item in items:
        symbol = QgsFillSymbol.createSimple({
            "color": item["color"],
            "outline_color": item["outline"],
            "outline_width": "0.15",
        })
        symbol.setOpacity(item["opacity"])
        filter_exp = f'"ETIPLAN" = \'{item["code"]}\''
        rule = QgsRuleBasedRenderer.Rule(symbol, 0, 0, filter_exp, item["label"])
        group_rule.appendChild(rule)
    root_rule.appendChild(group_rule)

# 5. Apply to layer
renderer = QgsRuleBasedRenderer(root_rule)
layer.setRenderer(renderer)
layer.triggerRepaint()

# 6. Refresh QGIS interface
if iface:
    iface.layerTreeView().refreshLayerSymbology(layer.id())
    iface.mapCanvas().refresh()

print(f"[SUCCESS] Applied hierarchical rule-based style to '{LAYER_NAME}' with {len(groups)} groups.")
