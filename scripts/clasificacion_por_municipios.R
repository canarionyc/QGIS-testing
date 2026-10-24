#%% 3. LA INTERSECCIÓN ESPACIAL (El cruce GDAL/OGR)
# Esto "corta" las manchas de suelo usando las fronteras de los municipios
intersectado <- st_intersection(suelo, municipios)

# 4. Agrupación y Cálculo de Áreas
# Asumiendo que tus columnas se llaman 'NOM_MUN' (municipio) y 'SUBCAT' (subcategoría de suelo)
resultado <- intersectado %>%
  group_by(NOM_MUN, SUBCAT) %>%
  # st_union une todos los polígonos inconexos de la misma categoría en un solo multipolígono por municipio
  summarise(geometry = st_union(geometry), .groups = 'drop') %>%
  mutate(
    # st_area devuelve un objeto 'units' en m2, lo pasamos a numérico y luego a hectáreas
    area_m2 = as.numeric(st_area(geometry)),
    area_ha = area_m2 / 10000
  )

# 5. Cálculo de Porcentajes Relativos
resultado <- resultado %>%
  group_by(NOM_MUN) %>%
  mutate(
    area_total_mun_ha = sum(area_ha),
    porcentaje_suelo = round((area_ha / area_total_mun_ha) * 100, 2)
  ) %>%
  ungroup()

# 6. Exportar el resultado final a Shapefile para tu presentación en QGIS
# Saldrá un shapefile con filas tipo: "Santa Cruz" | "SUC" | 500 ha | 15.5% | [Multipolygon]
st_write(resultado, "Municipios_Suelo_Analisis.shp", append = FALSE)

print("¡Proceso completado! Generado archivo 33x16 con áreas y porcentajes.")
