import urllib.request
import json

series_to_fetch = {
    "inmigracion_exterior": "EM1841733",
    "emigracion_exterior": "EM1919934",
    "saldo_exterior": "EM2416118",
    "saldo_interior": "EM2416119",
    "saldo_total": "EM2416117"
}

results = {}

for name, cod in series_to_fetch.items():
    url = f"https://servicios.ine.es/wstempus/js/ES/DATOS_SERIE/{cod}?nult=50"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            pts = {d["Anyo"]: d["Valor"] for d in data.get("Data", [])}
            results[name] = {
                "nombre": data.get("Nombre"),
                "data": pts
            }
            print(f"Fetched {name} ({cod}): {len(pts)} points")
    except Exception as e:
        print(f"Error fetching {name} ({cod}): {e}")

all_years = sorted(list(set(y for s in results.values() for y in s["data"])))
print("\nYear | Inmigración Ext. | Emigración Ext. | Saldo Ext. | Saldo Int. | Saldo Total")
print("-" * 75)
for y in all_years:
    inm = results.get("inmigracion_exterior", {}).get("data", {}).get(y, "-")
    emi = results.get("emigracion_exterior", {}).get("data", {}).get(y, "-")
    sext = results.get("saldo_exterior", {}).get("data", {}).get(y, "-")
    sint = results.get("saldo_interior", {}).get("data", {}).get(y, "-")
    stot = results.get("saldo_total", {}).get("data", {}).get(y, "-")
    print(f"{y:4d} | {str(inm):>16} | {str(emi):>15} | {str(sext):>10} | {str(sint):>10} | {str(stot):>11}")

with open("migration_sctf.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)
print("\nSaved to migration_sctf.json")
