import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
url = "https://datos.canarias.es/api/estadisticas/indicators/v1.0/indicators/POBLACION_00A14"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 QGIS/3.34'})
with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    print("Keys in indicator metadata:", data.keys())
    print("Geographical granularities:")
    for g in data.get("dimension", {}).get("GEOGRAPHICAL", {}).get("granularity", []):
        print("  -", g.get("code"), g.get("title", {}).get("es"))
