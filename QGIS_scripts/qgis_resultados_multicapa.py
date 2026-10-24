import json
import os
from qgis.core import QgsProject, QgsLayerTreeGroup

# --- CONFIGURACIÓN ---
GROUP_NAME = "Puentes" 
OUTPUT_FILE = "C:/dev/QGIS-testing/resultados_puentes_detallado.json"

def extract_from_group():
    root = QgsProject.instance().layerTreeRoot()
    group = root.findGroup(GROUP_NAME)
    
    if not group:
        print(f"ERROR: No se encontró el grupo '{GROUP_NAME}'.")
        return

    # 1. Obtenemos todas las capas DENTRO del grupo
    bridge_layers = [node.layer() for node in group.children() if node.nodeType() == 0] # 0 = Capa
    
    # 2. Obtenemos todas las capas del proyecto para intersectar (excluyendo las del grupo)
    all_layers = QgsProject.instance().mapLayers().values()
    bridge_layer_ids = [lyr.id() for lyr in bridge_layers]

    report = []

    print(f"Iniciando análisis de {len(bridge_layers)} capas de puentes...")

    for lyr in bridge_layers:
        if lyr is None or not lyr.isSpatial():
            continue
            
        print(f" > Procesando capa: {lyr.name()}")
        
        for feature in lyr.getFeatures():
            bridge_geom = feature.geometry()
            
            # Datos básicos del puente (usamos el nombre de la capa como nombre del puente)
            bridge_data = {
                "puente_nombre": lyr.name(),
                "coordenadas_wkt": bridge_geom.asPoint().asWkt() if bridge_geom.isMultipart() == False else "MultiPoint",
                "intersecciones": []
            }

            # 3. Intersectamos este punto con el resto de capas del mapa
            for other_layer in all_layers:
                # No nos intersectamos con nosotros mismos ni con otras capas del grupo "Puentes"
                if other_layer.id() in bridge_layer_ids or not other_layer.isSpatial():
                    continue
                
                # Para cada capa (EST, CAT, ZUSO...), buscamos qué hay debajo del puente
                for other_feat in other_layer.getFeatures():
                    if bridge_geom.intersects(other_feat.geometry()):
                        # Extraemos atributos saltándonos los valores nulos para limpiar el JSON
                        attrs = {fld.name(): other_feat.attribute(fld.name()) 
                                 for fld in other_layer.fields() 
                                 if other_feat.attribute(fld.name()) is not None}
                        
                        bridge_data["intersecciones"].append({
                            "capa_pgo": other_layer.name(),
                            "informacion": attrs
                        })
            
            report.append(bridge_data)

    # Guardar resultados
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=4)
    
    print(f"\n¡Hecho! Se han analizado los puentes y guardado en: {OUTPUT_FILE}")

extract_from_group()