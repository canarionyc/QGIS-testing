import psycopg2

conn = psycopg2.connect("dbname=fip_pgo user=postgres password=postgres1 host=localhost port=5432")
cur = conn.cursor()

print("--- Plazos de gestion y ejecucion in UAs ---")
cur.execute("""
    SELECT c.determinacion_codigo, d.nombre, c.valor_num, COUNT(*)
    FROM fip_entidades e
    JOIN fip_condiciones c ON e.codigo = c.entidad_codigo
    JOIN fip_determinaciones d ON c.determinacion_codigo = d.codigo
    WHERE e.tipo = 'UA' AND d.codigo IN ('0000000203', '0000001103')
    GROUP BY c.determinacion_codigo, d.nombre, c.valor_num
    ORDER BY c.determinacion_codigo, c.valor_num;
""")
for r in cur.fetchall():
    print(f"  Det {r[0]} ({r[1]}): {r[2]} meses -> {r[3]} UAs")

cur.close()
conn.close()
