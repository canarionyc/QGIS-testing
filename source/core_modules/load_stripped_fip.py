import json
import os
import psycopg2
from psycopg2.extras import execute_batch

def load_stripped_fip():
    json_path = r"C:\dev\QGIS-testing\data\Santa Cruz de Tenerife\PGO_20150811\fip_regimen_ua.json"
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Stripped JSON not found at {json_path}")

    print("=" * 60)
    print("STEP 1: CREATING / CONNECTING TO 'fip_pgo' DATABASE")
    print("=" * 60)

    # 1. Connect to default postgres to create fip_pgo database if not exists
    conn_default = psycopg2.connect("dbname=postgres user=postgres password=postgres1 host=localhost port=5432")
    conn_default.autocommit = True
    cur_default = conn_default.cursor()
    cur_default.execute("SELECT 1 FROM pg_database WHERE datname = 'fip_pgo';")
    if not cur_default.fetchone():
        cur_default.execute("CREATE DATABASE fip_pgo;")
        print("[OK] Database 'fip_pgo' created.")
    else:
        print("[OK] Database 'fip_pgo' already exists.")
    cur_default.close()
    conn_default.close()

    # 2. Connect to fip_pgo database
    conn = psycopg2.connect("dbname=fip_pgo user=postgres password=postgres1 host=localhost port=5432")
    conn.autocommit = True
    cur = conn.cursor()

    print("\n" + "=" * 60)
    print("STEP 2: ENABLING POSTGIS & CREATING TABLES")
    print("=" * 60)

    cur.execute("""
        CREATE EXTENSION IF NOT EXISTS postgis;

        DROP VIEW IF EXISTS v_unidades_actuacion CASCADE;
        DROP VIEW IF EXISTS v_sectores CASCADE;
        DROP VIEW IF EXISTS v_clasificacion_suelo CASCADE;

        DROP TABLE IF EXISTS fip_condiciones CASCADE;
        DROP TABLE IF EXISTS fip_entidades CASCADE;
        DROP TABLE IF EXISTS fip_determinaciones CASCADE;

        CREATE TABLE fip_entidades (
            codigo VARCHAR(50) PRIMARY KEY,
            padre_codigo VARCHAR(50),
            clave VARCHAR(100),
            nombre VARCHAR(255),
            tipo VARCHAR(50),
            clase_suelo VARCHAR(100),
            subclase_suelo VARCHAR(150),
            nivel INT,
            geom geometry(MultiPolygon, 23030)
        );

        CREATE INDEX idx_fip_entidades_geom ON fip_entidades USING GIST (geom);
        CREATE INDEX idx_fip_entidades_tipo ON fip_entidades (tipo);
        CREATE INDEX idx_fip_entidades_clase ON fip_entidades (clase_suelo);

        CREATE TABLE fip_determinaciones (
            codigo VARCHAR(50) PRIMARY KEY,
            padre_codigo VARCHAR(50),
            nombre VARCHAR(255),
            etiqueta VARCHAR(255),
            seccion VARCHAR(150),
            nivel INT
        );

        CREATE INDEX idx_fip_det_padre ON fip_determinaciones (padre_codigo);

        CREATE TABLE fip_condiciones (
            id SERIAL PRIMARY KEY,
            entidad_codigo VARCHAR(50) REFERENCES fip_entidades(codigo) ON DELETE CASCADE,
            determinacion_codigo VARCHAR(50),
            caso_codigo VARCHAR(50),
            valor TEXT,
            valor_num NUMERIC,
            valor_ref_codigo VARCHAR(50),
            valor_ref_nombre VARCHAR(255),
            texto TEXT
        );

        CREATE INDEX idx_fip_cond_ent ON fip_condiciones (entidad_codigo);
        CREATE INDEX idx_fip_cond_det ON fip_condiciones (determinacion_codigo);
    """)
    print("[OK] Tables created with spatial indices.")

    print("\n" + "=" * 60)
    print("STEP 3: PARSING & INSERTING STRIPPED FIP DATA")
    print("=" * 60)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    tramite = data["FIP"]["TRAMITE"]

    # 3.1 Extract Determinaciones
    det_list = []
    det_name_map = {}

    def parse_dets(node, parent_code=None, section_name="General", level=0):
        code = node.get("@codigo")
        name = node.get("@nombre")
        etiqueta = node.get("@etiqueta")
        det_name_map[code] = name
        det_list.append((code, parent_code, name, etiqueta, section_name, level))
        h = node.get("HIJAS", {}).get("DETERMINACION", [])
        if isinstance(h, dict): h = [h]
        for x in h:
            parse_dets(x, code, section_name if level > 0 else name, level + 1)

    for top_d in tramite["DETERMINACIONES"]["DETERMINACION"]:
        parse_dets(top_d, section_name=top_d.get("@nombre", "General"))

    print(f"Inserting {len(det_list)} determinaciones...")
    execute_batch(cur, """
        INSERT INTO fip_determinaciones (codigo, padre_codigo, nombre, etiqueta, seccion, nivel)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (codigo) DO NOTHING;
    """, det_list, page_size=500)
    print(f"[OK] {len(det_list)} determinaciones inserted.")

    # 3.2 Extract Entidades
    ent_list = []

    def classify_entity(clave, name):
        c_upper = clave.upper()
        n_upper = name.upper()
        if "GES_UA" in c_upper or "UNIDAD DE ACTUACI" in n_upper or "UA-" in n_upper or "UA " in n_upper:
            return "UA"
        if "GES_S" in c_upper or "SECTOR" in n_upper:
            return "SECTOR"
        if "DES" in c_upper or "AMB" in c_upper or "ÁMBITO" in n_upper or "AMBITO" in n_upper:
            return "AMBITO"
        if "CLA-" in c_upper:
            return "CLASIFICACION"
        if "SU-" in c_upper or "SU_SUB" in c_upper:
            return "SUELO_URBANO"
        if "SUR-" in c_upper or "SUR_SUB" in c_upper:
            return "SUELO_URBANIZABLE"
        if "RUS-" in c_upper or "RUS_SUB" in c_upper:
            return "SUELO_RUSTICO"
        if "GES-" in c_upper:
            return "GESTION"
        return "OTRO"

    def parse_ents(node, parent_code=None, path_names=[], level=0):
        code = node.get("@codigo")
        clave = node.get("@clave", "")
        name = node.get("@nombre", "")
        geom_wkt = node.get("GEOMETRIA")

        current_path = path_names + [name]
        tipo = classify_entity(clave, name)

        # Trace land classification from hierarchy
        clase_suelo = None
        subclase_suelo = None
        for p in current_path:
            p_low = p.lower()
            if "suelo urbano" in p_low:
                clase_suelo = "Suelo Urbano"
            elif "suelo urbanizable" in p_low:
                clase_suelo = "Suelo Urbanizable"
            elif "suelo rústico" in p_low or "suelo rustico" in p_low:
                clase_suelo = "Suelo Rústico"

            if "consolidado por la urbanización" in p_low or "consolidado" in p_low:
                if "no consolidado" in p_low:
                    subclase_suelo = "Suelo Urbano No Consolidado"
                else:
                    subclase_suelo = "Suelo Urbano Consolidado"
            elif "sectorizado" in p_low:
                if "no sectorizado" in p_low:
                    subclase_suelo = "Suelo Urbanizable No Sectorizado"
                else:
                    subclase_suelo = "Suelo Urbanizable Sectorizado"

        ent_list.append((code, parent_code, clave, name, tipo, clase_suelo, subclase_suelo, level, geom_wkt))

        h = node.get("HIJAS", {}).get("ENTIDAD", [])
        if isinstance(h, dict): h = [h]
        for x in h:
            parse_ents(x, code, current_path, level + 1)

    root_ent = tramite["ENTIDADES"]["ENTIDAD"]
    parse_ents(root_ent)

    print(f"Inserting {len(ent_list)} entidades...")
    for item in ent_list:
        code, parent_code, clave, name, tipo, clase, subclase, level, geom_wkt = item
        if geom_wkt:
            cur.execute("""
                INSERT INTO fip_entidades (codigo, padre_codigo, clave, nombre, tipo, clase_suelo, subclase_suelo, nivel, geom)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, ST_Multi(ST_GeomFromText(%s, 23030)))
                ON CONFLICT (codigo) DO NOTHING;
            """, (code, parent_code, clave, name, tipo, clase, subclase, level, geom_wkt))
        else:
            cur.execute("""
                INSERT INTO fip_entidades (codigo, padre_codigo, clave, nombre, tipo, clase_suelo, subclase_suelo, nivel, geom)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NULL)
                ON CONFLICT (codigo) DO NOTHING;
            """, (code, parent_code, clave, name, tipo, clase, subclase, level))
    print(f"[OK] {len(ent_list)} entidades inserted.")

    # 3.3 Extract Condiciones Urbanísticas
    cond_list = []
    raw_conds = tramite["CONDICIONES-URBANISTICAS"]["CONDICION-URBANISTICA"]
    for c in raw_conds:
        cod = c.get("CODIGO", {})
        e_code = cod.get("ENTIDAD", {}).get("@entidad")
        d_code = cod.get("DETERMINACION", {}).get("@determinacion")

        casos = c.get("CASOS", {}).get("CASO", [])
        if isinstance(casos, dict): casos = [casos]
        for cs in casos:
            caso_code = cs.get("@codigo")
            regs = cs.get("REGIMENES", {}).get("REGIMEN", []) if isinstance(cs.get("REGIMENES"), dict) else []
            if isinstance(regs, dict): regs = [regs]
            if not regs:
                cond_list.append((e_code, d_code, caso_code, None, None, None, None, None))
            else:
                for r in regs:
                    if not isinstance(r, dict): continue
                    val_str = r.get("VALOR")
                    val_num = None
                    if val_str:
                        try:
                            val_num = float(str(val_str).replace(",", "."))
                        except:
                            val_num = None

                    vr_code = r.get("VALOR-REFERENCIA", {}).get("@determinacion") if isinstance(r.get("VALOR-REFERENCIA"), dict) else None
                    vr_name = det_name_map.get(vr_code)

                    texto = None
                    reg_esp = r.get("REGIMENES-ESPECIFICOS", {}).get("REGIMEN-ESPECIFICO")
                    if isinstance(reg_esp, dict):
                        texto = reg_esp.get("TEXTO")
                    elif isinstance(reg_esp, list) and len(reg_esp) > 0 and isinstance(reg_esp[0], dict):
                        texto = reg_esp[0].get("TEXTO")

                    cond_list.append((e_code, d_code, caso_code, val_str, val_num, vr_code, vr_name, texto))

    print(f"Inserting {len(cond_list)} condiciones urbanísticas...")
    execute_batch(cur, """
        INSERT INTO fip_condiciones (
            entidad_codigo, determinacion_codigo, caso_codigo,
            valor, valor_num, valor_ref_codigo, valor_ref_nombre, texto
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
    """, cond_list, page_size=1000)
    print(f"[OK] {len(cond_list)} condiciones inserted.")

    print("\n" + "=" * 60)
    print("STEP 4: CREATING SPATIAL VIEWS FOR QGIS")
    print("=" * 60)

    cur.execute("""
        -- 1. View for Unidades de Actuación with execution systems and capacity metrics
        CREATE OR REPLACE VIEW v_unidades_actuacion AS
        SELECT 
            e.codigo,
            e.clave,
            e.nombre,
            e.clase_suelo,
            e.subclase_suelo,
            MAX(CASE WHEN c.determinacion_codigo = '0000000219' THEN c.valor_ref_nombre END) AS sistema_ejecucion,
            MAX(CASE WHEN c.determinacion_codigo = '0000001091' THEN c.valor_num END) AS edificabilidad_m2c,
            MAX(CASE WHEN c.determinacion_codigo = '0000001063' THEN c.valor_num END) AS aprovechamiento_medio,
            MAX(CASE WHEN c.determinacion_codigo = '0000001093' THEN c.valor_num END) AS superficie_suelo_m2,
            MAX(CASE WHEN c.determinacion_codigo = '0000001046' THEN c.valor_num END) AS superficie_lucrativo_m2,
            MAX(CASE WHEN c.determinacion_codigo = '0000001081' THEN c.valor_ref_nombre END) AS uso_global,
            MAX(CASE WHEN c.determinacion_codigo = '0000001088' THEN c.valor_ref_nombre END) AS tipo_ambito_gestion,
            e.geom
        FROM fip_entidades e
        LEFT JOIN fip_condiciones c ON e.codigo = c.entidad_codigo
        WHERE e.tipo = 'UA'
        GROUP BY e.codigo, e.clave, e.nombre, e.clase_suelo, e.subclase_suelo, e.geom;

        -- 2. View for Sectores
        CREATE OR REPLACE VIEW v_sectores AS
        SELECT 
            e.codigo,
            e.clave,
            e.nombre,
            e.clase_suelo,
            e.subclase_suelo,
            MAX(CASE WHEN c.determinacion_codigo = '0000001091' THEN c.valor_num END) AS edificabilidad_m2c,
            MAX(CASE WHEN c.determinacion_codigo = '0000001093' THEN c.valor_num END) AS superficie_suelo_m2,
            MAX(CASE WHEN c.determinacion_codigo = '0000001081' THEN c.valor_ref_nombre END) AS uso_global,
            e.geom
        FROM fip_entidades e
        LEFT JOIN fip_condiciones c ON e.codigo = c.entidad_codigo
        WHERE e.tipo = 'SECTOR'
        GROUP BY e.codigo, e.clave, e.nombre, e.clase_suelo, e.subclase_suelo, e.geom;

        -- 3. View for Land Classification Polygons
        CREATE OR REPLACE VIEW v_clasificacion_suelo AS
        SELECT 
            codigo,
            clave,
            nombre,
            tipo,
            clase_suelo,
            subclase_suelo,
            geom
        FROM fip_entidades
        WHERE tipo IN ('CLASIFICACION', 'SUELO_URBANO', 'SUELO_URBANIZABLE', 'SUELO_RUSTICO')
          AND geom IS NOT NULL;
    """)
    print("[OK] Spatial views 'v_unidades_actuacion', 'v_sectores', and 'v_clasificacion_suelo' created.")

    # 4. Verify counts
    print("\n" + "=" * 60)
    print("STEP 5: VERIFICATION & SUMMARY")
    print("=" * 60)
    for tbl in ["fip_entidades", "fip_determinaciones", "fip_condiciones", "v_unidades_actuacion", "v_sectores", "v_clasificacion_suelo"]:
        cur.execute(f"SELECT COUNT(*) FROM {tbl};")
        cnt = cur.fetchone()[0]
        print(f"  * {tbl}: {cnt} rows")

    cur.close()
    conn.close()
    print("\n[SUCCESS] FIP database ingestion completed successfully!")

if __name__ == "__main__":
    load_stripped_fip()
