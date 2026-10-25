import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
url = "https://datos.canarias.es/api/estadisticas/indicators/v1.0/indicators?limit=5"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 QGIS/3.34'})
with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    print("Keys in response:", data.keys())
    items = data.get('items', [])
    print(f"Total items returned: {len(items)}")
    if items:
        first = items[0]
        print("First indicator code/id:", first.get('id'), first.get('code'), first.get('title'))
        ind_code = first.get('id') or first.get('code')
        
        # Now test the data URL that istacqgis tries to call:
        # url = url_root + path + "/" + resource
        # resource = indicatorcode + "/data" + "?representation=" + representation + "&granularity=" + granularity + "&fields=" + fields
        test_url = f"https://datos.canarias.es/api/estadisticas/indicators/v1.0/indicators/{ind_code}/data?representation=&granularity=&fields="
        print("\nTesting indicator data URL:", test_url)
        try:
            req_data = urllib.request.Request(test_url, headers={'User-Agent': 'Mozilla/5.0 QGIS/3.34'})
            with urllib.request.urlopen(req_data, timeout=10, context=ctx) as resp_data:
                print("Status:", resp_data.status)
                body = resp_data.read()
                print("Length:", len(body))
                data_json = json.loads(body.decode('utf-8'))
                print("Data JSON keys:", data_json.keys())
        except urllib.error.HTTPError as he:
            print("HTTPError:", he.code, he.reason)
            print("HTTP response:", he.read().decode('utf-8')[:500])
        except Exception as e:
            print("Error:", type(e).__name__, e)
