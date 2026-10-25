import zipfile
import shapefile
import io

catastro_zip = r"c:\dev\QGIS-testing\data\Santa Cruz de Tenerife\Catastro - 38900uA 38015 SANTA CRUZ DE TENERIFE\38900uA_38015_23012026_CONSTRU.ZIP"

with zipfile.ZipFile(catastro_zip, 'r') as z:
    for name in z.namelist():
        if name.endswith('.dbf'):
            dbf_bytes = z.read(name)
            shp_name = name.replace('.dbf', '.shp')
            shp_bytes = z.read(shp_name)
            shx_name = name.replace('.dbf', '.shx')
            shx_bytes = z.read(shx_name)
            
            sf = shapefile.Reader(shp=io.BytesIO(shp_bytes), dbf=io.BytesIO(dbf_bytes), shx=io.BytesIO(shx_bytes))
            print(f"Catastro CONSTRU records: {len(sf)}")
            fields = [f[0] for f in sf.fields[1:]]
            print(f"Fields in CONSTRU: {fields}")
            rec = sf.record(0)
            print(f"Sample record: {dict(zip(fields, rec))}")
            break
