import json
import os
from qgis.core import QgsProject, QgsCoordinateTransform, QgsCoordinateReferenceSystem, QgsFeatureRequest

# --- CONFIGURACIÓN ---
GROUP_NAME = "Puentes" 
OUTPUT_FILE = "C:/dev/QGIS-testing/debug_puentes.json"
TOLERANCIA_METROS = 1.0  # Ampliamos la búsqueda 1 metro alrededor de la línea

def debug_identify_results():
    project = QgsProject.instance()
    root = project.layerTreeRoot()
    group = root.findGroup(GROUP_NAME)
    
    if not group:
        print(f"--- ERROR: No se encontró el grupo '{GROUP_NAME}' ---")
        return

    # 1. Identificar capas
    bridge_layers = [node.layer() for node in group.children() if node.nodeType() == 0]
    all_layers = [lyr for lyr in project.mapLayers().values() if lyr.isSpatial() and lyr.name() not in [l.name() for l in bridge_layers]]
    
    print(f"--- INICIANDO ESCANEO DE {len(bridge_layers)} PUENTES ---")
    print(f"Sistema de Referencia del Proyecto: {project.crs().authid()}")
    
    report = []
    project_crs = project.crs()

    for b_layer in bridge_layers:
        if b_layer is None: continue
        
        print(f"\n[PUENTE] Analizando capa: {b_layer.name()}")
        print(f"  - CRS Original: {b_layer.crs().authid()}")
        print(f"  - Elementos encontrados: {b_layer.featureCount()}")
        
        b_transform = QgsCoordinateTransform(b_layer.crs(), project_crs, project)
        
        for b_feat in b_layer.getFeatures():
            # Geometría y transformación
            b_geom = b_feat.geometry()
            b_geom.transform(b_transform)
            
            # Aplicar un pequeño buffer para emular el "clic" del ratón
            b_geom_buffered = b_geom.buffer(TOLERANCIA_METROS, 5)
            
            bridge_entry = {
                "puente": b_layer.name(),
                "hallazgos": []
            }

            for info_layer in all_layers:
                # Filtrar capas de fondo (imágenes) que no tienen tabla de atributos
                if info_layer.type() != 0: continue # Solo capas vectoriales
                
                i_transform = QgsCoordinateTransform(info_layer.crs(), project_crs, project)
                
                # Verbosity: mostrar qué capa estamos escaneando
                print(f"    > Cruzando con: {info_layer.name()}...", end=" ")
                
                count = 0
                # Usamos un filtro de rectángulo (Bounding Box) para ir más rápido
                request = QgsFeatureRequest().setFilterRect(b_geom_buffered.boundingBox())
                
                for i_feat in info_layer.getFeatures(request):
                    i_geom = i_feat.geometry()
                    i_geom.transform(i_transform)
                    
                    if b_geom_buffered.intersects(i_geom):
                        attrs = {f.name(): i_feat.attribute(f.name()) 
                                 for f in info_layer.fields() 
                                 if i_feat.attribute(f.name()) is not None}
                        
                        bridge_entry["hallazgos"].append({
                            "capa": info_layer.name(),
                            "data": attrs
                        })
                        count += 1
                
                print(f"[{count} coincidencias]")

            report.append(bridge_entry)

    # Guardar
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=4)
    
    print(f"\n--- PROCESO COMPLETADO ---")
    print(f"Archivo guardado: {OUTPUT_FILE}")

debug_identify_results()