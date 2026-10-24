import os
from qgis.core import QgsProject

# Get the path of the current QGIS project
project_path = QgsProject.instance().fileName()

if project_path:
    # Extract just the folder directory
    project_dir = os.path.dirname(project_path)
    # Set it as the new working directory
    os.chdir(project_dir)
    print(f"Working directory changed to: {os.getcwd()}")
else:
    print("Please save your QGIS project first!")