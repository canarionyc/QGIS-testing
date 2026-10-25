import sys
sys.path.append(r"C:\Users\tglla\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins")

from PyQt5.QtCore import QCoreApplication
app = QCoreApplication.instance()
if not app:
    app = QCoreApplication(sys.argv)

from istacqgis.controllers.istacpy import istacpy

# Query indicators that have SECTIONS or DISTRICTS
inds = istacpy.get_indicators(limit=400)
items = inds.get('items', [])
print(f"Total indicators retrieved: {len(items)}")

detailed = []
for it in items:
    code = it.get('id')
    # Check if granularities can be fetched or if we check title
    title = it.get('title', {}).get('es', '')
    if any(w in title.lower() for w in ['secci', 'distrit', 'barrio', 'censo']):
        print(f"Candidate: {code} -> {title}")
