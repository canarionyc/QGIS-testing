#%% 
import json
import re
import pandas as pd
import geopandas as gpd
from shapely import wkt

#%% --- Configuration ---
# Update this path to your actual FIP.json file
FIP_JSON_PATH = r"C:\dev\QGIS-testing\data\Santa Cruz de Tenerife\PGO\fip.json"
# Santa Cruz de Tenerife usually uses EPSG:25828 (REGCAN95 / UTM zone 28N)
# or EPSG:4083. Verify with your plan documentation.
PROJECTION = "EPSG:25828" 

BARRANCO_REGEX = re.compile(r"barranco", re.IGNORECASE)

def find_entities(node, parent_codigo="", current_path=""):
    results = []
    if isinstance(node, dict):
        my_codigo = node.get("@codigo", "")
        my_nombre = node.get("@nombre", "")
        my_geom = node.get("GEOMETRIA", "")
        
        if my_nombre:
            new_path = f"{current_path} > {my_nombre}" if current_path else my_nombre
        else:
            new_path = current_path
            
        # Filter: Name contains "barranco" AND has geometry
        # Note: You can add more logic here to exclude "Condiciones..." if needed
        if my_nombre and BARRANCO_REGEX.search(my_nombre) and my_geom:
            results.append({
                "codigo": my_codigo,
                "nombre": my_nombre,
                "parent_codigo": parent_codigo,
                "hierarchy_path": new_path,
                "wkt": my_geom
            })
            
        next_parent = my_codigo if my_codigo else parent_codigo
        for key, value in node.items():
            results.extend(find_entities(value, next_parent, new_path))
            
    elif isinstance(node, list):
        for item in node:
            results.extend(find_entities(item, parent_codigo, current_path))
            
    return results

#%% --- Main Execution ---
print("Loading JSON file...")
with open(FIP_JSON_PATH, "r", encoding="utf-8") as f:
    fip_data = json.load(f)

print("Extracting entities...")
data_list = find_entities(fip_data)

if not data_list:
    print("No entities found.")
else:
    print(f"Found {len(data_list)} entities. Converting to Spatial Data...")
    
    # 1. Create a standard Pandas DataFrame
    df = pd.DataFrame(data_list)
    
    # 2. Convert WKT strings to real Shapely geometries
    df['geometry'] = df['wkt'].apply(wkt.loads)
    
    # 3. Create a GeoDataFrame
    gdf = gpd.GeoDataFrame(df, geometry='geometry', crs=PROJECTION)
    
    # 4. Remove the raw WKT text column (not needed in a spatial file)
    gdf = gdf.drop(columns=['wkt'])
    
    # 5. Export to GeoPackage (Recommended for QGIS)
    output_filename = "barrancos_santos.gpkg"
    gdf.to_file(output_filename, driver="GPKG")
    
    print(f"Success! File saved as: {output_filename}")
    print("You can now drag and drop this file directly into QGIS.")
# %%
