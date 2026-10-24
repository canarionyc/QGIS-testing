#%% setup
import xml.etree.ElementTree as ET
import psycopg2

# 1. Connect to your local PostgreSQL database
# Change 'postgres' and 'your_password' to your actual database credentials
conn = psycopg2.connect("dbname=postgres user=postgres password=postgres1 host=localhost")
conn.autocommit = True  # This makes it so we don't have to manually commit
cur = conn.cursor()

#%% Create the tables (Drop them first if they exist so we can rerun safely)
cur.execute("""
    -- TURN ON THE GIS ENGINE
    CREATE EXTENSION IF NOT EXISTS postgis;
    
    DROP TABLE IF EXISTS fip_condiciones;
    DROP TABLE IF EXISTS fip_entidades CASCADE;
    DROP TABLE IF EXISTS fip_determinaciones;

    CREATE TABLE fip_entidades (
        codigo VARCHAR(50) PRIMARY KEY,
        clave VARCHAR(50),
        nombre VARCHAR(255),
        geom geometry(MultiPolygon, 23030)
    );

    CREATE TABLE fip_determinaciones (
        codigo VARCHAR(50) PRIMARY KEY,
        nombre VARCHAR(255),
        etiqueta VARCHAR(255)
    );

    CREATE TABLE fip_condiciones (
        id SERIAL PRIMARY KEY,
        entidad_codigo VARCHAR(50), -- REFERENCES fip_entidades(codigo),
        determinacion_codigo VARCHAR(50) -- REFERENCES fip_determinaciones(codigo)
    );
""")

#%% 2. Load the FIP XML file (Update this path to where your file is saved!)
# xml_path = r"C:\dev\QGIS-testing\data\La Palma\3b0c42ab8f17416f562370b30089191e\fip.xml"
xml_path=r"C:\dev\QGIS-testing\data\Santa Cruz de Tenerife\Plan General de Ordenación de Santa Cruz de Tenerife\fip.xml"
# Parse with the correct XML parser
parser = ET.XMLParser(encoding="iso-8859-1")
tree = ET.parse(xml_path, parser=parser)
root = tree.getroot()

#%% 3. Parse and Insert ENTIDADES
print("Inserting Entidades...")

for entidad in root.findall('.//ENTIDADES/ENTIDAD'):
    codigo = entidad.get('codigo')
    clave = entidad.get('clave')
    nombre = entidad.get('nombre')

    geom_elem = entidad.find('GEOMETRIA')
    wkt_geom = geom_elem.text if geom_elem is not None else None

    if wkt_geom:
        cur.execute("""
            INSERT INTO fip_entidades (codigo, clave, nombre, geom) 
            VALUES (%s, %s, %s, ST_GeomFromText(%s, 23030))
            ON CONFLICT (codigo) DO NOTHING;
        """, (codigo, clave, nombre, wkt_geom))

#%% 4. Parse and Insert DETERMINACIONES
print("Inserting Determinaciones...")
denominaciones = root.findall('.//DETERMINACIONES/DETERMINACION/nombre')

for det in root.findall('.//DETERMINACIONES/DETERMINACION'):
    codigo = det.get('codigo')
    nombre = det.get('nombre')
    etiqueta = det.get('etiqueta')

    cur.execute("""
        INSERT INTO fip_determinaciones (codigo, nombre, etiqueta) 
        VALUES (%s, %s, %s)
        ON CONFLICT (codigo) DO NOTHING;
    """, (codigo, nombre, etiqueta))

#%% 5. Parse and Insert CONDICIONES
print("Inserting Condiciones...")
for condicion in root.findall('.//CONDICIONES-URBANISTICAS/CONDICION-URBANISTICA'):
    ent_elem = condicion.find('.//ENTIDAD')
    det_elem = condicion.find('.//DETERMINACION')

    if ent_elem is not None and det_elem is not None:
        ent_codigo = ent_elem.get('entidad')
        det_codigo = det_elem.get('determinacion')

        cur.execute("""
            INSERT INTO fip_condiciones (entidad_codigo, determinacion_codigo) 
            VALUES (%s, %s);
        """, (ent_codigo, det_codigo))

cur.close()
conn.close()
print("FIP successfully loaded into PostgreSQL!")