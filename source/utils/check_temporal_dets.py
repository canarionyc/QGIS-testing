import psycopg2

conn = psycopg2.connect("dbname=fip_pgo user=postgres password=postgres1 host=localhost port=5432")
cur = conn.cursor()

print("--- Columns of fip_determinaciones ---")
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'fip_determinaciones';
""")
for c, dt in cur.fetchall():
    print(f"  {c}: {dt}")

print("\n--- Check Determinaciones for temporal concepts (plazo, programacion, ejecucion, cuatrienio, ano, fecha) ---")
cur.execute("""
    SELECT codigo, nombre, etiqueta, seccion 
    FROM fip_determinaciones 
    WHERE nombre ILIKE '%plazo%' 
       OR nombre ILIKE '%fecha%' 
       OR nombre ILIKE '%año%' 
       OR nombre ILIKE '%cuatrienio%' 
       OR nombre ILIKE '%etapa%' 
       OR nombre ILIKE '%fase%' 
       OR nombre ILIKE '%programaci%'
       OR nombre ILIKE '%vigencia%'
       OR nombre ILIKE '%temporal%'
       OR nombre ILIKE '%ejecuci%'
    ORDER BY nombre;
""")
dets = cur.fetchall()
print(f"Found {len(dets)} matching determinaciones:")
for r in dets:
    print(f"  [{r[0]}] {r[1]} (etiqueta: {r[2]}, seccion: {r[3]})")

# If any determinaciones match, check if any UA has conditions pointing to them!
if dets:
    det_codes = tuple(d[0] for d in dets)
    cur.execute("""
        SELECT c.determinacion_codigo, d.nombre, c.valor, c.valor_num, c.valor_ref_nombre, COUNT(*)
        FROM fip_condiciones c
        JOIN fip_determinaciones d ON c.determinacion_codigo = d.codigo
        WHERE c.determinacion_codigo IN %s
        GROUP BY c.determinacion_codigo, d.nombre, c.valor, c.valor_num, c.valor_ref_nombre;
    """, (det_codes,))
    print("\n--- Conditions attached to these determinaciones ---")
    for r in cur.fetchall():
        print(f"  Det {r[0]} ({r[1]}): valor='{r[2]}', num={r[3]}, ref='{r[4]}' -> {r[5]} entities")

cur.close()
conn.close()
