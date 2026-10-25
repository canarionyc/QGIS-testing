import urllib.request
import urllib.parse
import json
import ssl

ctx = ssl.create_default_context()
url = "https://datos.canarias.es/api/estadisticas/indicators/v1.0/subjects"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 QGIS/3.34'})
with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    items = data.get('items', [])
    print(f"Testing {len(items)} subjects...")
    for it in items[:8]:
        sid = it.get('id')
        title_es = it.get('title', {}).get('es')
        q = f'subjectCode EQ "{sid}"'
        q_enc = urllib.parse.quote(q)
        q_url = f"https://datos.canarias.es/api/estadisticas/indicators/v1.0/indicators?q={q_enc}&limit=10"
        try:
            r = urllib.request.Request(q_url, headers={'User-Agent': 'Mozilla/5.0 QGIS/3.34'})
            with urllib.request.urlopen(r, timeout=10, context=ctx) as resp_q:
                res_data = json.loads(resp_q.read().decode('utf-8'))
                print(f"Subject: {sid} ({title_es}) -> {res_data.get('total')} indicators")
        except Exception as e:
            print(f"Subject: {sid} ({title_es}) -> ERROR: {e}")
