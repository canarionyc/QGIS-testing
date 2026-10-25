import urllib.request
import json
import ssl

ctx = ssl.create_default_context()

urls = [
    "https://datos.canarias.es/api/estadisticas/indicators/v1.0/subjects",
    "https://datos.canarias.es/api/estadisticas/indicators/v1.0/indicators",
    "http://datos.canarias.es/api/estadisticas/indicators/v1.0/indicators",
    "https://www.gobiernodecanarias.org/istac/api/estadisticas/indicators/v1.0/indicators",
]

for url in urls:
    print("Testing:", url)
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 QGIS/3.34'})
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            print("  Status:", resp.status)
            body = resp.read()
            print("  Length:", len(body))
            try:
                data = json.loads(body.decode('utf-8'))
                print("  JSON parsed successfully, keys/len:", type(data), len(data) if isinstance(data, (list, dict)) else 'scalar')
            except Exception as e:
                print("  JSON parse error:", e, "Snippet:", body[:200])
    except Exception as e:
        print("  Request error:", type(e).__name__, e)
