import urllib.request

req = urllib.request.Request(
    'https://www.boe.es/buscar/act.php?id=BOE-A-2017-10295',
    headers={'User-Agent': 'Mozilla/5.0'}
)
with urllib.request.urlopen(req, timeout=10) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

idx = 0
for i in range(5):
    idx = html.find('Sistemas de ejecuci', idx + 1)
    if idx == -1: break
    print(f"Occurrence {i+1} at {idx}:")
    print(html[idx-150:idx+150])
    print("="*40)
