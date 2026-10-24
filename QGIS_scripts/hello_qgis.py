#%% general setup

import sys; print('Python %s on %s' % (sys.version, sys.platform))

from pprint import pprint

# pprint.pprint(globals())
# pprint.pprint(locals())
# pprint.pprint(dir())
pprint(sys.path)

import os; print(os.getcwd())

#%% QGIS imports
from qgis.core import QgsApplication

#%% 1. Set the prefix path to your OSGeo4W QGIS installation
QgsApplication.setPrefixPath("C:/OSGeo4W/apps/qgis-ltr", True)

# 2. Initialize the QGIS application (False means we don't need the GUI/interface)
qgs = QgsApplication([], False)
qgs.initQgis()

# 3. Do something QGIS-specific!
print("Hello QGIS!")
print("Successfully loaded QGIS environment.")
print(QgsApplication.showSettings())

# 4. Safely close the application and clean up memory
qgs.exitQgis()