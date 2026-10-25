import urllib.request
import json

url = 'https://www.ine.es/geoserver/ogc/features/v1/collections/WMS_INE_SECCIONES_G01:Secciones_2024/items?limit=1&f=json'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 QGIS/3.34'})
with urllib.request.urlopen(req, timeout=10) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    feat = data.get('features', [])[0]
    print("OGC API feature keys:", list(feat.keys()))
    print("Properties:", feat.get('properties'))
