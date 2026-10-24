import json
import csv

def extract_barrancos(node, parent_codigo="", current_path=""):
    results = []

    # XML-to-JSON tools sometimes create a list (if multiple siblings) or a dict (if single)
    if isinstance(node, list):
        for item in node:
            results.extend(extract_barrancos(item, parent_codigo, current_path))
            
    elif isinstance(node, dict):
        # 1. Is this an ENTIDAD?
        if "@codigo" in node:
            my_codigo = node.get("@codigo", "")
            my_nombre = node.get("@nombre", "")
            my_geom = node.get("GEOMETRIA", "")
            
            # Update the breadcrumb trail
            new_path = f"{current_path} > {my_nombre}" if current_path else my_nombre
            
            # 2. Is it a Barranco with geometry?
            if "barranco" in my_nombre.lower() and my_geom:
                results.append({
                    "codigo": my_codigo,
                    "nombre": my_nombre,
                    "parent_codigo": parent_codigo,
                    "hierarchy_path": new_path,
                    "geometria_wkt": my_geom
                })
            
            # 3. Does it have children (HIJAS)? Keep digging!
            if "HIJAS" in node and "ENTIDAD" in node["HIJAS"]:
                results.extend(extract_barrancos(node["HIJAS"]["ENTIDAD"], my_codigo, new_path))
                
        # If it's not an ENTIDAD, search its children anyway
        else:
            for key, value in node.items():
                if isinstance(value, (dict, list)):
                    results.extend(extract_barrancos(value, parent_codigo, current_path))
                    
    return results

# --- Main Execution ---
print("Loading massive JSON file...")
fip_json_path = "C:\\dev\\QGIS-testing\\data\\Santa Cruz de Tenerife\\Plan General de Ordenación de Santa Cruz de Tenerife\\fip.json"
with open(fip_json_path, "r", encoding="utf-8") as f:
    fip_data = json.load(f)

print("Crawling tree for Barrancos...")
# Start the recursive search from the root of the document
barrancos = extract_barrancos(fip_data)

print(f"Found {len(barrancos)} Barrancos. Saving to CSV...")
with open("barrancos_extract.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["codigo", "nombre", "parent_codigo", "hierarchy_path", "geometria_wkt"])
    writer.writeheader()
    writer.writerows(barrancos)

print("Done! Ready for QGIS/PostGIS.")