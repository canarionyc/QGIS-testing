import json
import os
from qgis.core import QgsProject, QgsCoordinateTransform, QgsFeatureRequest
from qgis.PyQt.QtCore import QVariant, QDateTime, QDate

def fix_value(val):
    if isinstance(val, QVariant):
        if val.isNull(): return None
        val = val.value()
    if isinstance(val, (QDateTime, QDate)):
        return val.toString("yyyy-MM-dd HH:mm:ss")
    return val

# --- CONFIGURACIÓN ---
GROUP_NAME = "Puentes" 
OUTPUT_FILE = "C:/dev/QGIS-testing/resultados_puentes_final.json"
TOLERANCIA_METROS = 1.5 

# Capas que queremos ignorar explícitamente aunque estén encendidas
BLACKLIST = ["AMB", "OrtoExpress Urbana 10-12.5 cm/pixel", "TRA"]

def export_refined_results():
    project = QgsProject.instance()
    root = project.layerTreeRoot()
    group = root.findGroup(GROUP_NAME)
    
    if not group:
        print(f"--- ERROR: No se encontró el grupo '{GROUP_NAME}' ---")
        return

    bridge_layers = [node.layer() for node in group.findLayers() if node.layer() is not None]
    bridge_ids = [b.id() for b in bridge_layers]
    
    all_layers = []
    print("--- FILTRANDO CAPAS ACTIVAS ---")
    for lyr in project.mapLayers().values():
        # Filtro 1: Debe ser vectorial (tipo 0)
        if lyr.type() != 0: 
            continue
            
        # Filtro 2: No debe estar en la lista negra ni ser un puente
        if lyr.name() in BLACKLIST or lyr.id() in bridge_ids:
            continue
            
        # Filtro 3: Solo capas que estén VISIBLES en el panel de capas
        node = root.findLayer(lyr.id())
        if node and node.isVisible():
            all_layers.append(lyr)
            print(f"  [+] Incluyendo: {lyr.name()}")
        else:
            print(f"  [-] Saltando (Invisibles/Restringidas): {lyr.name()}")

    report = []
    project_crs = project.crs()

    print(f"\n--- INICIANDO EXPORTACIÓN DE {len(bridge_layers)} PUENTES ---")

    for b_layer in bridge_layers:
        print(f"[PROCESANDO] {b_layer.name()}")
        b_transform = QgsCoordinateTransform(b_layer.crs(), project_crs, project)
        bridge_entry = {"puente": b_layer.name(), "hallazgos": []}

        for b_feat in b_layer.getFeatures():
            b_geom = b_feat.geometry()
            b_geom.transform(b_transform)
            b_geom_search = b_geom.buffer(TOLERANCIA_METROS, 5)

            for info_layer in all_layers:
                i_transform = QgsCoordinateTransform(info_layer.crs(), project_crs, project)
                request = QgsFeatureRequest().setFilterRect(b_geom_search.boundingBox())
                
                for i_feat in info_layer.getFeatures(request):
                    i_geom = i_feat.geometry()
                    i_geom.transform(i_transform)
                    
                    if b_geom_search.intersects(i_geom):
                        attrs = {f.name(): fix_value(i_feat.attribute(f.name())) 
                                 for f in info_layer.fields() 
                                 if i_feat.attribute(f.name()) is not None}
                        bridge_entry["hallazgos"].append({
                            "capa": info_layer.name(),
                            "datos": attrs
                        })

        report.append(bridge_entry)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=4)
    print(f"\n--- PROCESO FINALIZADO CON ÉXITO ---")

export_refined_results()