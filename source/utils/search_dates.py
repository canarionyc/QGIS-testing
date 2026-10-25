import psycopg2

def check_dates():
    for db in ["postgres", "fip_pgo"]:
        try:
            conn = psycopg2.connect(f"dbname={db} user=postgres password=postgres1 host=localhost port=5432")
            cur = conn.cursor()
            print(f"\n========================================================")
            print(f"DATABASE: {db}")
            print(f"========================================================")

            # Find date/time columns across all tables in non-system schemas
            cur.execute("""
                SELECT table_schema, table_name, column_name, data_type
                FROM information_schema.columns
                WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
                  AND (data_type ILIKE '%date%' 
                       OR data_type ILIKE '%time%' 
                       OR column_name ILIKE '%date%'
                       OR column_name ILIKE '%fecha%'
                       OR column_name ILIKE '%ano%'
                       OR column_name ILIKE '%year%')
                ORDER BY table_schema, table_name, ordinal_position;
            """)
            date_cols = cur.fetchall()
            print(f"Found {len(date_cols)} potential date/time columns:")
            for s, t, c, d in date_cols:
                print(f"  {s}.{t} -> {c} ({d})")

            # Let's also check distinct values of those date columns if count is reasonable
            for s, t, c, d in date_cols:
                try:
                    cur.execute(f'SELECT COUNT(DISTINCT "{c}"), MIN("{c}"), MAX("{c}") FROM "{s}"."{t}" WHERE "{c}" IS NOT NULL;')
                    cnt, min_v, max_v = cur.fetchone()
                    print(f"    [Values in {s}.{t}.{c}]: {cnt} distinct values, range: {min_v} to {max_v}")
                    if cnt and cnt <= 10:
                        cur.execute(f'SELECT DISTINCT "{c}" FROM "{s}"."{t}" WHERE "{c}" IS NOT NULL ORDER BY "{c}";')
                        vals = [r[0] for r in cur.fetchall()]
                        print(f"      distinct: {vals}")
                except Exception as e:
                    print(f"    [Error checking {s}.{t}.{c}]: {e}")
                    conn.rollback()

            # Check if there are tramites or any tables with "tramite" in their name
            cur.execute("""
                SELECT table_schema, table_name
                FROM information_schema.tables
                WHERE table_name ILIKE '%tramite%' OR table_name ILIKE '%fip%' OR table_name ILIKE '%ua%'
                ORDER BY table_schema, table_name;
            """)
            print("\nRelevant tables (tramite, fip, ua):")
            for s, t in cur.fetchall():
                print(f"  {s}.{t}")

            cur.close()
            conn.close()
        except Exception as e:
            print(f"Failed to connect to db '{db}': {e}")

if __name__ == "__main__":
    check_dates()
