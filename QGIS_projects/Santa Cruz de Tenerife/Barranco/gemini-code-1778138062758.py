import json
import csv

# Los códigos que identificaste como clave
TARGET_CODES = ["0000000795", "0000000141"]

def find_nodes_with_key(node, key_name):
    """Busca recursivamente cualquier objeto que tenga una clave específica."""
    results = []
    if isinstance(node, dict):
        if key_name in node:
            results.append(node)
        for v in node.values():
            results.extend(find_nodes_with_key(v, key_name))
    elif isinstance(node, list):
        for item in node:
            results.extend(find_nodes_with_key(item, key_name))
    return results

def extract_rules():
    print("Cargando fip.json (100MB)...")
    with open("fip.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Mapear todas las DETERMINACIONES del plan
    print("Mapeando el libro de reglas (Determinaciones)...")
    all_objects = find_nodes_with_key(data, "@codigo")
    
    # Creamos un buscador rápido: código -> nombre de la regla
    # En el FIP, las determinaciones suelen tener @nombre y a veces @apartado
    det_lookup = {
        obj["@codigo"]: obj.get("@nombre", "Sin nombre") 
        for obj in all_objects 
        if "@nombre" in obj
    }

    # 2. Buscar nuestras entidades objetivo
    print(f"Buscando conexiones para: {TARGET_CODES}")
    target_entities = [obj for obj in all_objects if obj.get("@codigo") in TARGET_CODES]

    rules_found = []

    for ent in target_entities:
        ent_name = ent.get("@nombre", "Entidad desconocida")
        ent_code = ent.get("@codigo")
        
        # En el FIP, los vínculos están en el nodo 'VALORES'
        valores_container = ent.get("VALORES", {})
        if valores_container:
            # Pueden ser uno solo (dict) o varios (list)
            valores = valores_container.get("VALOR", [])
            if isinstance(valores, dict): valores = [valores]
            
            for v in valores:
                det_id = v.get("@determinacion")
                rule_name = det_lookup.get(det_id, f"Regla desconocida ({det_id})")
                
                rules_found.append({
                    "entidad_codigo": ent_code,
                    "entidad_nombre": ent_name,
                    "determinacion_codigo": det_id,
                    "norma_aplicada": rule_name
                })

    # 3. Guardar el resultado
    if rules_found:
        with open("normativa_barranco.csv", "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["entidad_codigo", "entidad_nombre", "determinacion_codigo", "norma_aplicada"])
            writer.writeheader()
            writer.writerows(rules_found)
        print(f"¡Éxito! Se han encontrado {len(rules_found)} reglas aplicables.")
        print("Revisa 'normativa_barranco.csv' para ver los nombres de las leyes/usos.")
    else:
        print("No se encontraron vínculos directos a DETERMINACION en estos nodos.")

if __name__ == "__main__":
    extract_rules()