import json

def inspect_file(fname):
    fpath = f'c:/dev/QGIS-testing/data/ISTAC/{fname}'
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"\n==================== {fname} ====================")
    dim = data.get('dimension', {})
    print("Dimensions:", list(dim.keys()))
    for dname, dval in dim.items():
        rep = dval.get('representation', {})
        size = rep.get('size')
        idx = rep.get('index', {})
        print(f"  {dname} (size {size}):")
        # Print a few samples of index
        items = list(idx.items())
        if dname == 'GEOGRAPHICAL':
            sc = [item for item in items if '38038' in item[0]]
            print(f"    Santa Cruz in GEOGRAPHICAL: {sc}")
        elif len(items) <= 15:
            print(f"    {items}")
        else:
            print(f"    Sample: {items[:3]} ... {items[-3:]}")

inspect_file('population_all.json')
inspect_file('alojatur_poblacion_tur_etc.json')
inspect_file('renta.json')
