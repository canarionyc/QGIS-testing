-- =====================================================================
-- PGO Santa Cruz de Tenerife - PostGIS Analysis Queries
-- Database: fip_pgo | Schema: public | SRID: 23030 (ED50 / UTM Zone 28N)
-- =====================================================================

-- 1. Overview of all Unidades de Actuación with execution systems & buildable area
SELECT 
    clave,
    nombre,
    clase_suelo,
    subclase_suelo,
    sistema_ejecucion,
    edificabilidad_m2c,
    aprovechamiento_medio,
    ROUND(ST_Area(geom)::numeric, 1) AS area_geom_m2,
    uso_global
FROM v_unidades_actuacion
ORDER BY edificabilidad_m2c DESC NULLS LAST;

-- 2. Summary by Land Classification (UAs count, total buildable area, total polygon area)
SELECT 
    COALESCE(subclase_suelo, clase_suelo) AS categoria_suelo,
    COUNT(*) AS total_uas,
    ROUND(SUM(edificabilidad_m2c)::numeric, 0) AS total_edificabilidad_m2c,
    ROUND(SUM(ST_Area(geom))::numeric, 0) AS total_superficie_suelo_m2
FROM v_unidades_actuacion
GROUP BY COALESCE(subclase_suelo, clase_suelo)
ORDER BY total_edificabilidad_m2c DESC NULLS LAST;

-- 3. Summary by Execution System (Sistemas de Ejecución)
SELECT 
    COALESCE(sistema_ejecucion, 'No especificado') AS sistema_ejecucion,
    COUNT(*) AS num_uas,
    ROUND(SUM(edificabilidad_m2c)::numeric, 0) AS total_edificabilidad_m2c
FROM v_unidades_actuacion
GROUP BY sistema_ejecucion
ORDER BY num_uas DESC;

-- 4. Sectores overview
SELECT 
    clave,
    nombre,
    clase_suelo,
    edificabilidad_m2c,
    superficie_suelo_m2,
    ROUND(ST_Area(geom)::numeric, 1) AS area_calculada_m2,
    uso_global
FROM v_sectores
ORDER BY edificabilidad_m2c DESC NULLS LAST;

-- 5. Inspect conditions and statutory deadlines (plazos) for a specific UA
SELECT 
    e.clave,
    e.nombre,
    d.nombre AS determinacion,
    c.valor,
    c.valor_ref_nombre,
    c.texto
FROM fip_condiciones c
JOIN fip_entidades e ON c.entidad_codigo = e.codigo
JOIN fip_determinaciones d ON c.determinacion_codigo = d.codigo
WHERE e.clave LIKE '%GES_UA%'
  AND d.codigo = '0000000203' -- Plazos para la gestión y ejecución
ORDER BY e.clave;
