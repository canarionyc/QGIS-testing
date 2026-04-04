# %% ANÁLISIS DE CLASES DE SUELO POR MUNICIPIO EN CANARIAS
# install.packages(c("sf", "dplyr"))
library(sf)
library(dplyr)
print(getwd())
print(.libPaths())


#%% suelo Santa Cruz de Tenerife
#suelo <- st_read("/vsizip/C:/dev/QGIS-testing/data/gobcan_suelo.zip")
suelo_sf <- st_read(r"(C:\dev\QGIS-testing\data\140613-pgo-sct-sipu\02SIST\CLA.shp)")
# suelo <- st_transform(suelo, 32628)
suelo_sf <- st_make_valid(suelo_sf)
print(suelo <- st_drop_geometry(suelo_sf))




#%% 
# install.packages("data.table")
library(data.table)
library(sf)

# 1. Aseguramos que sea un data.table
setDT(suelo)

suelo[, area_m2 := as.numeric(st_area(geometry))]
suelo[, area_ha := area_m2 / 10000]
# 2. Agregación con el ejemplar mayor y disolución espacial
suelo_agrupado <- suelo[, .(
  area_ha = sum(area_ha, na.rm = TRUE),
  
  # Extraemos el nombre (o etiqueta) del polígono más grande del grupo
  ejmplr_m_c  = CODIGO[which.max(area_ha)], 
  
  # Si prefieres el texto descriptivo, usa:
  ejmplr_m_h = area_ha[which.max(area_ha)],
  
  # Disolución espacial (une todos los polígonos del grupo en uno solo)
  # geometry = st_union(geometry)
  geometry = st_union(st_buffer(geometry, dist = 0.01))
  
), by = .(ETIQUETA, TXTPLAN)]; print(suelo_agrupado)

setorderv(suelo_agrupado, "area_ha", order = -1L)

str(suelo_agrupado)


# saveRDS(suelo_agrupado, "data/desglose_santa_cruz.rds")
#%%add main category
# install.packages("stringr")
library(stringr)

suelo_agrupado[, CLASE_MAIN := fcase(
  grepl("Urbano", TXTPLAN ), "Suelo Urbano",
  grepl("Urbanizable", TXTPLAN ), "Suelo Urbanizable",
  grepl("Rústico", TXTPLAN ), "Suelo Rústico",
  default = "Otros / Sistemas Generales"
)]; print(suelo_agrupado)

str(suelo_agrupado)

#%% Luego guardas el shapefile con st_write()
suelo_agrupado_sf <- st_as_sf(suelo_agrupado)
print(getwd())
?mf_export
mapsf::mf_export(
  x = suelo_agrupado_sf, 
  filename = "img/suelo_agrupado.png", 
  width = 2000,     
  res = 300
)

st_write(suelo_agrupado_sf, "data/suelo_agrupado.gpkg", append = FALSE)


#%% agrupar by main class
suelo_reagrupado <- suelo_agrupado[, .( 
  area_ha = sum(area_ha, na.rm = TRUE),
  
  # Extraemos el nombre (o etiqueta) del polígono más grande del grupo
  ejmplr_m_c  = ejmplr_m_c[which.max(area_ha)], 
  
  # Si prefieres el texto descriptivo, usa:
  ejmplr_m_h = area_ha[which.max(area_ha)],
  
  # Disolución espacial (une todos los polígonos del grupo en uno solo)
  # geometry = st_union(geometry)
  geometry = st_union(st_buffer(geometry, dist = 0.01))
  
), by = .(CLASE_MAIN)]; print(suelo_reagrupado)

setorderv(suelo_reagrupado, "area_ha", order = -1L)


print(suelo_reagrupado)

#%% Luego guardas el shapefile con st_write()
# Ver el resultado
# 3. Restauramos la clase sf para poder mapear o exportar
suelo_reagrupado_sf <- st_as_sf(suelo_reagrupado)

str(suelo_reagrupado_sf)
# st_write(suelo_reagrupado_sf, "data/suelo_reagrupado.shp", append = FALSE, delete_layer = TRUE)
# saveRDS(suelo_reagrupado, "data/desglose_santa_cruz.rds")

# El estándar moderno: un solo archivo, sin límites de caracteres, a prueba de balas
st_write(
  suelo_reagrupado_sf, 
  "data/suelo_reagrupado.gpkg", 
  delete_dsn = TRUE # Borra el archivo previo si existe
)


#%% Visualización rápida con mapview
#install.packages("mapview")
# library(mapview)

# # Inspeccionar rápidamente
# mapview::mapview(suelo_reagrupado, zcol = "CLASE_MAIN", legend = TRUE, viewer.suppress = FALSE) + 
#   mapview::mapview(municipios, color = "black", alpha.regions = 0, lwd = 1, legend = FALSE)

#%%
# install.packages("mapsf")
library(mapsf)
library(sf)


# 1. Definimos el tema ANTES de exportar
mf_theme("default")
# ?mf_export
# ?png
# 2. Abrimos el lienzo y le indicamos que use el motor gráfico Cairo
#debugonce(mf_export)
class(suelo_reagrupado_sf)
mf_export(
  x = suelo_reagrupado_sf, 
  filename = "img/suelo_reagrupado.png", 
  width = 2000,     
  res = 300
)
# 3. Dibujamos los polígonos
mf_map(
  x = suelo_reagrupado_sf,
  var = "CLASE_MAIN",
  type = "typo", 
  val_order = c("Suelo Urbano", "Suelo Urbanizable", "Suelo Rústico"),
  pal = c("#E31A1C", "#FD8D3C", "#33A02C"), 
  #border = NA, # <--- Esto elimina las líneas negras internas y externas
  leg_title = "Clasificación del Suelo",
  leg_pos = "bottomright"
)

# 4. Añadimos el cajetín, norte y escala
mf_layout(
  title = "Clasificación del Suelo - Santa Cruz de Tenerife",
  credits = "Fuente: SIPU Canarias | Procesado con data.table y mapsf",
  arrow = FALSE,   
  scale = FALSE   
)

# 5. Guardar y cerrar
dev.off()

#%%
# install.packages("maptiles")
library(mapsf)
library(maptiles)
library(sf)

# 1. Definimos el servidor XYZ del PNOA (que contiene los vuelos de IDECanarias)
url_idecanarias <- list(
  src = "https://tms-pnoa-ma.idee.es/1.0.0/pnoa-ma/{z}/{x}/{y}.jpeg",
  q = "",
  cit = "© IGN / GRAFCAN"
)

# 2. Descargamos las teselas ajustadas a la extensión exacta de tu municipio
# Un zoom = 14 o 15 da muy buena resolución. (Cuidado con zoom >= 17, tardará mucho)
ortofoto <- get_tiles(
  x = suelo_reagrupado_sf, 
  provider = url_idecanarias, 
  zoom = 14, 
  crop = TRUE
)

# 3. Preparamos el tema y el lienzo
mf_theme("default")
mf_export(
  x = suelo_reagrupado_sf, 
  filename = "img/mapa_santa_cruz_orto.png", 
  width = 2000,     
  res = 300,        
  type = "cairo"
)

# 4. PASO CLAVE: Dibujamos PRIMERO la ortofoto como fondo
mf_raster(ortofoto)

# 5. Dibujamos los polígonos SOBRE la ortofoto
mf_map(
  x = suelo_reagrupado_sf,
  var = "CLASE_MAIN",
  type = "typo", 
  val_order = c("Suelo Urbano", "Suelo Urbanizable", "Suelo Rústico"),
  pal = c("#E31A1C", "#FD8D3C", "#33A02C"),
  border = NA,          # Seguimos ocultando los 'slivers' internos
  alpha = 0.6,          # <-- IMPORTANTE: 60% de opacidad para dejar ver la ortofoto
  add = TRUE,           # <-- IMPORTANTE: add = TRUE le dice que no borre la foto previa
  leg_title = "Clasificación del Suelo",
  leg_pos = "bottomleft"
)

# 6. Añadimos elementos cartográficos (con fondo blanco para que se lean sobre la foto)
mf_layout(
  title = "Clasificación del Suelo - Santa Cruz de Tenerife",
  credits = "Fuente: SIPU Canarias | Ortofoto: PNOA/GRAFCAN",
  arrow = TRUE,   
  scale = TRUE    
)

# 7. Guardar y cerrar
dev.off()

#%% ggplot2
#install.packages("ggplot2")
# library(ggplot2)

# # Crear un mapa coloreado por la clasificación del suelo
# mi_mapa <- ggplot(data = suelo) +
#   # geom_sf dibuja los polígonos. 'color = NA' quita los bordes negros para que se vea limpio
#   geom_sf(aes(fill = TXTPLAN), color = NA) +
#   theme_minimal() +
#   labs(
#     title = "Clasificación del Suelo - Santa Cruz de Tenerife",
#     fill = "Categoría"
#   ) +
#   theme(legend.position = "right", legend.text = element_text(size = 7))
# mi_mapa



# ggsave("img/Clasificación del Suelo - Santa Cruz de Tenerife.png", plot = mi_mapa, dpi = 300, width = 10, height = 6)
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