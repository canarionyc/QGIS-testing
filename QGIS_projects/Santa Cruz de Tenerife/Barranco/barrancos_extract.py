#%% setup
import json
import csv
import re

import os
print("Current working directory:", os.getcwd())

# %% find entities with "barranco" in their name, regardless of case, and that have a geometry
# Compile a regex to find "barranco" anywhere in the string, case-insensitive
# This covers "Barranco", "BARRANCO", "barranco santos", etc.
BARRANCO_REGEX = re.compile(r"barranco", re.IGNORECASE)

def find_entities(node, parent_codigo="", current_path=""):
    results = []
    
    if isinstance(node, dict):
        # 1. Safely grab attributes if they exist in this dictionary
        my_codigo = node.get("@codigo", "")
        my_nombre = node.get("@nombre", "")
        my_geom = node.get("GEOMETRIA", "")
        
        # 2. Update the hierarchy path ONLY if this node has a name
        if my_nombre:
            new_path = f"{current_path} > {my_nombre}" if current_path else my_nombre
        else:
            new_path = current_path
            
        # 3. XPath // matching: Does this node have a name matching the regex AND a geometry?
        if my_nombre and BARRANCO_REGEX.search(my_nombre) and my_geom:
            results.append({
                "codigo": my_codigo,
                "nombre": my_nombre,
                "parent_codigo": parent_codigo,
                "hierarchy_path": new_path,
                "geometria_wkt": my_geom
            })
            
        # 4. Determine the parent ID for the next level down
        next_parent = my_codigo if my_codigo else parent_codigo
        
        # 5. Keep digging recursively into EVERY key and value in this dictionary
        for key, value in node.items():
            results.extend(find_entities(value, next_parent, new_path))
            
    elif isinstance(node, list):
        # If we hit a list, just iterate through it and pass down the current path/parent
        for item in node:
            results.extend(find_entities(item, parent_codigo, current_path))
            
    return results

# --- Main Execution ---
print("Loading massive JSON file...")
fip_json_path = "C:\\dev\\QGIS-testing\\data\\Santa Cruz de Tenerife\\PGO\\fip.json"

with open(fip_json_path, "r", encoding="utf-8") as f:
    fip_data = json.load(f)

print("Crawling tree recursively using Regex...")
barrancos = find_entities(fip_data)

print(f"Found {len(barrancos)} Barrancos. Saving to CSV...")
if barrancos:
    with open("barrancos_extract.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["codigo", "nombre", "parent_codigo", "hierarchy_path", "geometria_wkt"])
        writer.writeheader()
        writer.writerows(barrancos)
    print("Done! CSV is ready to drop into QGIS.")
else:
    print("Still found 0. Please verify the JSON file name or structure.")
# %%
