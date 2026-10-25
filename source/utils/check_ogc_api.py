import urllib.request
import json

url = 'https://www.ine.es/geoserver/ogc/features/v1/collections?f=json'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 QGIS/3.34'})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        colls = data.get('collections', [])
        print(f"Total OGC API Collections: {len(colls)}")
        for c in colls:
            cid = c.get('id')
            ctit = c.get('title')
            print(f"  - {cid}: {ctit}")
except Exception as e:
    print("Error:", e)
