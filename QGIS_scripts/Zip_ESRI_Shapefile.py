import os
import zipfile
from qgis.utils import iface

# Get the currently selected layer
layer = iface.activeLayer()

if not layer:
    print("[ERROR] Please click on a layer in the Layers Panel first!")
else:
    # Get the file path of the layer
    source_path = layer.source().split("|")[0] # Clean up the path just in case
    base_path, _ = os.path.splitext(source_path)
    
    # Define where the zip will be saved
    zip_filepath = f"{base_path}.zip"
    
    # Common shapefile extensions to look for
    extensions = ['.shp', '.shx', '.dbf', '.prj', '.cpg', '.qpj', '.sbn', '.sbx']
    
    try:
        with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
            files_zipped = 0
            for ext in extensions:
                file_to_zip = f"{base_path}{ext}"
                if os.path.exists(file_to_zip):
                    # Add to zip, but without the full folder path structure
                    zipf.write(file_to_zip, arcname=os.path.basename(file_to_zip))
                    files_zipped += 1
                    
        print(f"[SUCCESS] Zipped {files_zipped} files into: {zip_filepath}")
    except Exception as e:
        print(f"[ERROR] Could not zip files: {e}")