import psycopg2

conn = psycopg2.connect("dbname=fip_pgo user=postgres password=postgres1 host=localhost port=5432")
cur = conn.cursor()

print("--- All determinaciones attached to UAs ---")
cur.execute("""
    SELECT d.codigo, d.nombre, d.seccion, COUNT(DISTINCT e.codigo) as n_uas
    FROM fip_entidades e
    JOIN fip_condiciones c ON e.codigo = c.entidad_codigo
    JOIN fip_determinaciones d ON c.determinacion_codigo = d.codigo
    WHERE e.tipo = 'UA'
    GROUP BY d.codigo, d.nombre, d.seccion
    ORDER BY n_uas DESC;
""")
for r in cur.fetchall():
    print(f"  Det {r[0]}: {r[1]} ({r[2]}) -> {r[3]} UAs")

print("\n--- Check if any of these conditions contain text or values resembling dates or years ---")
cur.execute("""
    SELECT d.nombre, c.valor, c.valor_ref_nombre, c.texto, count(*)
    FROM fip_entidades e
    JOIN fip_condiciones c ON e.codigo = c.entidad_codigo
    JOIN fip_determinaciones d ON c.determinacion_codigo = d.codigo
    WHERE e.tipo = 'UA'
      AND (c.valor ~ '[12][90][0-9]{2}' 
           OR c.texto ~ '[12][90][0-9]{2}'
           OR c.valor_ref_nombre ~ '[12][90][0-9]{2}')
    GROUP BY d.nombre, c.valor, c.valor_ref_nombre, c.texto;
""")
matches = cur.fetchall()
print(f"Found {len(matches)} conditions matching 4-digit year pattern:")
for r in matches:
    print(f"  Det: {r[0]} | val: {r[1]} | ref: {r[2]} | txt: {r[3][:60] if r[3] else None} (cnt: {r[4]})")

cur.close()
conn.close()
