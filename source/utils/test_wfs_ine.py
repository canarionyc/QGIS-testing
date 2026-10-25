import urllib.request
import urllib.parse
import json

cql = urllib.parse.quote("CUMUN='38038'")
url = f"https://www.ine.es/geoserver/WMS_INE_SECCIONES_G01/wfs?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetFeature&TYPENAME=WMS_INE_SECCIONES_G01:Secciones_2024&COUNT=5&CQL_FILTER={cql}&outputFormat=application/json"

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 QGIS/3.34'})
with urllib.request.urlopen(req, timeout=15) as resp:
    data = json.loads(resp.read().decode('utf-8'))

print("Features returned:", len(data.get('features', [])))
if data.get('features'):
    feat = data['features'][0]
    print("Properties:", feat['properties'])
    print("Geometry type:", feat['geometry']['type'])
    print("Coordinate sample:", feat['geometry']['coordinates'][0][0][:2])
