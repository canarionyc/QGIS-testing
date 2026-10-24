import json
import os
from qgis.core import QgsProject, QgsCoordinateTransform, QgsFeatureRequest
from qgis.PyQt.QtCore import QVariant, QDateTime, QDate

# Función mejorada para convertir datos de QGIS a formatos estándar de Python/JSON
def fix_value(val):
    # Manejar el tipo QVariant (muy común en proveedores OGR/GML)
    if isinstance(val, QVariant):
        if val.isNull():
            return None
        val = val.value()

    # Manejar fechas y tiempos (que JSON no acepta de forma nativa)
    if isinstance(val, (QDateTime, QDate)):
        return val.toString("yyyy-MM-dd HH:mm:ss")
    
    # Si el valor es una lista o dict (raro en atributos pero posible), procesar recursivamente
    if isinstance(val, list):
        return [fix_value(i) for i in val]
        
    return val

# --- CONFIGURACIÓN ---
GROUP_NAME = "Puentes" 
OUTPUT_FILE = "C:/dev/QGIS-testing/resultados_puentes_final.json"
TOLERANCIA_METROS = 1.5 

def export_clean_results():
    project = QgsProject.instance()
    root = project.layerTreeRoot()
    group = root.findGroup(GROUP_NAME)
    
    if not group:
        print(f"--- ERROR: No se encontró el grupo '{GROUP_NAME}' ---")
        return

    # Buscamos todas las capas de puentes recursivamente
    layer_nodes = group.findLayers()
    bridge_layers = [node.layer() for node in layer_nodes if node.layer() is not None]
    
    # Capas de información (PGO), excluyendo las que están en el grupo Puentes
    bridge_ids = [b.id() for b in bridge_layers]
    # all_layers = [lyr for lyr in project.mapLayers().values() 
    #               if lyr.isSpatial() and lyr.id() not in bridge_ids]
    # Sustituye la línea donde definimos 'all_layers' por esta:
    # Obtenemos la instancia del árbol de capas para consultar propiedades de la GUI
    root = project.layerTreeRoot()

    all_layers = []
    for lyr in project.mapLayers().values():
        # 1. ¿Es espacial?
        # 2. ¿No es uno de los puentes?
        # 3. ¿Es "Identificable" en el árbol de capas?
        if lyr.isSpatial() and lyr.id() not in bridge_ids:
            node = root.findLayer(lyr.id())
            # Verificamos la propiedad custom 'identifiable' que QGIS guarda en el nodo
            is_identifiable = node.customProperty("identify") != "0" 
            
            if is_identifiable:
                all_layers.append(lyr)
    
    report = []
    project_crs = project.crs()

    print(f"--- INICIANDO EXPORTACIÓN DE {len(bridge_layers)} PUENTES ---")

    for b_layer in bridge_layers:
        print(f"[PROCESANDO] {b_layer.name()}")
        
        # Saltamos si no es vectorial (ej. una ortofoto que esté en el grupo por error)
        if b_layer.type() != 0: continue

        b_transform = QgsCoordinateTransform(b_layer.crs(), project_crs, project)
        bridge_entry = {"puente": b_layer.name(), "hallazgos": []}

        for b_feat in b_layer.getFeatures():
            b_geom = b_feat.geometry()
            b_geom.transform(b_transform)
            # El buffer crea el "área de contacto" para la línea del puente
            b_geom_search = b_geom.buffer(TOLERANCIA_METROS, 5)

            for info_layer in all_layers:
                if info_layer.type() != 0: continue 
                
                i_transform = QgsCoordinateTransform(info_layer.crs(), project_crs, project)
                request = QgsFeatureRequest().setFilterRect(b_geom_search.boundingBox())
                
                for i_feat in info_layer.getFeatures(request):
                    i_geom = i_feat.geometry()
                    i_geom.transform(i_transform)
                    
                    if b_geom_search.intersects(i_geom):
                        # Aplicamos fix_value a cada atributo para evitar el error de QVariant
                        attrs = {f.name(): fix_value(i_feat.attribute(f.name())) 
                                 for f in info_layer.fields() 
                                 if i_feat.attribute(f.name()) is not None}
                        
                        bridge_entry["hallazgos"].append({
                            "capa": info_layer.name(),
                            "datos": attrs
                        })

        report.append(bridge_entry)

    # Guardar a archivo
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=4)
    
    print(f"\n--- PROCESO FINALIZADO ---")
    print(f"Resultados guardados en: {OUTPUT_FILE}")

export_clean_results()