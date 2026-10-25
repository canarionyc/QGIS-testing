import psycopg2
import os
import glob

def inspect_all():
    # 1. Inspect PostgreSQL fip_pgo
    conn = psycopg2.connect("dbname=fip_pgo user=postgres password=postgres1 host=localhost port=5432")
    cur = conn.cursor()
    
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
    """)
    tables = [r[0] for r in cur.fetchall()]
    print(f"All tables in fip_pgo (public): {tables}")
    
    for t in tables:
        cur.execute("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position;
        """, (t,))
        cols = cur.fetchall()
        print(f"\nTable: {t}")
        for c in cols:
            print(f"  {c[0]} : {c[1]}")
            
    # Sample some rows from fip_entidades and v_unidades_actuacion
    print("\nSample fip_entidades (5 rows):")
    cur.execute("SELECT * FROM fip_entidades LIMIT 5;")
    for r in cur.fetchall():
        print(r)
        
    print("\nSample v_unidades_actuacion (5 rows):")
    cur.execute("SELECT * FROM v_unidades_actuacion LIMIT 5;")
    for r in cur.fetchall():
        print(r)

    cur.close()
    conn.close()

    # 2. Check FIP files on disk in c:\dev\QGIS-testing
    print("\nSearching for FIP files or XMLs in c:\\dev\\QGIS-testing:")
    for root, dirs, files in os.walk(r"c:\dev\QGIS-testing"):
        for f in files:
            if any(ext in f.lower() for ext in ['.fip', '.xml', '.gml', '.zip', '.tar']):
                fpath = os.path.join(root, f)
                size_mb = os.path.getsize(fpath) / (1024 * 1024)
                print(f"  {fpath} ({size_mb:.2f} MB)")

if __name__ == "__main__":
    inspect_all()
