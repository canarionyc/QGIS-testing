-- sanity check
SELECT COUNT(*) AS total_entidades FROM fip_entidades;
SELECT COUNT(*) AS total_determinaciones FROM fip_determinaciones;
SELECT COUNT(*) AS total_condiciones FROM fip_condiciones;    

-- Safe way to view the table
SELECT codigo, clave, nombre
FROM fip_entidades;

SELECT * FROM fip_entidades LIMIT 10;

CREATE VIEW fip_entidades_datos AS
SELECT codigo, clave, nombre
FROM fip_entidades;

-- 1. The "QGIS Master View" (Mapping the Data
SELECT
    e.clave,
    e.nombre AS entidad_nombre,
    d.nombre AS determinacion_nombre
    --, e.geom
FROM fip_entidades e
         JOIN fip_condiciones c ON e.codigo = c.entidad_codigo
         LEFT JOIN fip_determinaciones d ON c.determinacion_codigo = d.codigo
-- WHERE e.fip_id = ?
;

--2. Area Statistics by Category (The Pivot Table)
SELECT
    d.nombre AS categoria_urbanistica,
    COUNT(e.codigo) AS total_poligonos,
    SUM(ST_Area(e.geom)) AS area_total_m2
FROM fip_entidades e
         JOIN fip_condiciones c ON e.codigo = c.entidad_codigo
         JOIN fip_determinaciones d ON c.determinacion_codigo = d.codigo
GROUP BY d.nombre
ORDER BY area_total_m2 DESC;