import json

path = r"C:\dev\QGIS-testing\data\Santa Cruz de Tenerife\PGO_20150811\fip.json"

with open(path, "r", encoding="utf-8", errors="ignore") as f:
    data = json.load(f)

fip = data.get("FIP", {})
print("FIP attributes:")
for k, v in fip.items():
    if k.startswith("@"):
        print(f"  {k}: {v}")
    elif isinstance(v, dict):
        print(f"  {k} (dict keys): {list(v.keys())[:10]}")

tramite = fip.get("TRAMITE", {})
for k, v in tramite.items():
    if k.startswith("@"):
        print(f"  TRAMITE {k}: {v}")
    elif isinstance(v, dict):
        print(f"  TRAMITE {k}: dict with keys {list(v.keys())}")
        if "TEXTO" in v or "NOMBRE" in v:
            print(f"    Sample: {str(v)[:200]}")
    elif isinstance(v, list):
        print(f"  TRAMITE {k}: list of len {len(v)}")

# Check INSTRUMENTO / AMBITO if present
for section in ["AMBITOS", "ORGANIGRAMA", "DETERMINACIONES", "ENTIDADES", "DOCUMENTOS"]:
    if section in tramite:
        val = tramite[section]
        if isinstance(val, dict):
            for subk, subv in val.items():
                if isinstance(subv, list):
                    print(f"  tramite[{section}][{subk}]: {len(subv)} items")
                else:
                    print(f"  tramite[{section}][{subk}]: {type(subv)}")
