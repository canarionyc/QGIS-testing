import sys
sys.path.append(r"C:\Users\tglla\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins")

from PyQt5.QtWidgets import QApplication
app = QApplication.instance()
if not app:
    app = QApplication([])

from istacqgis.controllers import resources, istacpy

url = "https://datos.canarias.es/api/estadisticas/indicators/v1.0/indicators/POLICIA_LOCAL_EFECTIVOS/data?representation=&granularity=&fields="
print("Testing get_content with url:", url)
res = resources.get_content(url)
print("Result type:", type(res))
if isinstance(res, str):
    print("Result is str! Length:", len(res))
    if len(res) == 0:
        print("RESULT IS EMPTY STRING! QNetworkAccessManager error!")
else:
    print("Result is dict! Keys:", list(res.keys()))
