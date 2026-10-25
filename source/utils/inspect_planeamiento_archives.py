import os
import zipfile
import re

planeamiento_dir = r"c:\dev\QGIS-testing\data\Santa Cruz de Tenerife\Planeamiento"

print("=== CHECKING PLANEAMIENTO ARCHIVES IN SANTA CRUZ ===")
zips = [f for f in os.listdir(planeamiento_dir) if f.endswith('.zip')]

for zname in sorted(zips):
    zpath = os.path.join(planeamiento_dir, zname)
    size_mb = os.path.getsize(zpath) / (1024 * 1024)
    # Check filename date prefix (e.g. 140613 -> 2014-06-13, 170913 -> 2017-09-13, etc.)
    m = re.match(r'^(\d{2})(\d{2})(\d{2})-(.*)\.zip$', zname)
    if m:
        yy, mm, dd, rest = m.groups()
        year = f"20{yy}" if int(yy) < 50 else f"19{yy}"
        date_str = f"{year}-{mm}-{dd}"
        print(f"\nArchive: {zname} ({size_mb:.2f} MB)")
        print(f"  Extracted Date: {date_str} | Instrument: {rest}")
    else:
        print(f"\nArchive: {zname} ({size_mb:.2f} MB) - no standard YYMMDD prefix")

    try:
        with zipfile.ZipFile(zpath, 'r') as zf:
            namelist = zf.namelist()
            fip_files = [n for n in namelist if 'fip' in n.lower() or n.endswith('.xml')]
            shp_files = [n for n in namelist if n.endswith('.shp')]
            print(f"    Contents: {len(namelist)} files. FIP/XMLs: {fip_files[:3]}, SHPs: {len(shp_files)}")
            # If there's a fip.xml, check its FECHA
            for fip_name in fip_files:
                if fip_name.endswith('.xml'):
                    try:
                        with zf.open(fip_name) as f:
                            head = f.read(500).decode('iso-8859-1', errors='ignore')
                            fm = re.search(r'FECHA="([^"]+)"', head)
                            if fm:
                                print(f"      {fip_name} -> FIP FECHA={fm.group(1)}")
                    except Exception as e:
                        pass
    except Exception as e:
        print(f"    Error reading zip: {e}")
