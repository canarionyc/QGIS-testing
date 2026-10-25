import psycopg2

conn = psycopg2.connect("dbname=fip_pgo user=postgres password=postgres1 host=localhost port=5432")
cur = conn.cursor()

print("--- View Definition: v_unidades_actuacion ---")
cur.execute("""
    SELECT pg_get_viewdef('v_unidades_actuacion'::regclass, true);
""")
print(cur.fetchone()[0])

print("\n--- Any other views or tables in fip_pgo ---")
cur.execute("""
    SELECT table_name, table_type 
    FROM information_schema.tables 
    WHERE table_schema = 'public';
""")
for r in cur.fetchall():
    print(r)

cur.close()
conn.close()
