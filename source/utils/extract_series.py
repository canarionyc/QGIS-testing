import json

def get_series(fname, geo_code='38038', measure_code='ABSOLUTE'):
    fpath = f'c:/dev/QGIS-testing/data/ISTAC/{fname}'
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    dim = data['dimension']
    geo_idx = dim['GEOGRAPHICAL']['representation']['index'][geo_code]
    meas_idx = dim['MEASURE']['representation']['index'][measure_code]
    
    n_geo = dim['GEOGRAPHICAL']['representation']['size']
    n_time = dim['TIME']['representation']['size']
    n_meas = dim['MEASURE']['representation']['size']
    
    time_index = dim['TIME']['representation']['index']
    obs = data['observation']
    
    # In JSON-stat / ISTAC flattening order:
    # Look at loop from data.py:
    # index = 0
    # for i in range(GEOGRAPHICAL):
    #   for j in range(TIME):
    #     for k in range(MEASURE):
    #       val = obs[index]
    
    results = {}
    for time_str, t_idx in time_index.items():
        flat_idx = geo_idx * (n_time * n_meas) + t_idx * n_meas + meas_idx
        val = obs[flat_idx] if flat_idx < len(obs) else None
        results[time_str] = val
        
    return results

pop_series = get_series('population_all.json')
tur_series = get_series('alojatur_poblacion_tur_etc.json')
renta_series = get_series('renta.json')

print("=== POPULATION (population_all.json) for Santa Cruz de Tenerife (38038) ===")
for yr in sorted(pop_series.keys()):
    print(f"  {yr}: {pop_series[yr]}")

print("\n=== TOURISTIC POPULATION (alojatur_poblacion_tur_etc.json) for 38038 ===")
for yr in sorted(tur_series.keys()):
    print(f"  {yr}: {tur_series[yr]}")

print("\n=== RENTA (renta.json) for 38038 ===")
for yr in sorted(renta_series.keys()):
    print(f"  {yr}: {renta_series[yr]}")
