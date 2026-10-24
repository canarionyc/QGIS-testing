
# %% Visualización rápida con mapview
#install.packages("mapview")
# library(mapview)

# # Inspeccionar rápidamente
# mapview::mapview(suelo_reagrupado, zcol = "CLASE_MAIN", legend = TRUE, viewer.suppress = FALSE) +
#   mapview::mapview(municipios, color = "black", alpha.regions = 0, lwd = 1, legend = FALSE)


# %%
suelo_agrupado_png <- "img/suelo_agrupado.png"
if (!file.exists(suelo_agrupado_png)) {
  print(
    "Archivo no encontrado. Ejecuta el script 'land_class_by_muni.R' para generar el archivo 'suelo_agrupado.png' en la carpeta 'img'."
  )

  ?mf_export
  mapsf::mf_export(
    x = suelo_agrupado,
    filename = suelo_agrupado_png,
    width = 2000,
    res = 300
  )

  mf_map(
    x = suelo_agrupado,
    var = "ETIQUETA",
    type = "typo",
    val_order = names(color_mapping),
    pal = color_mapping,
    #border = NA, # <--- Esto elimina las líneas negras internas y externas
    leg_title = "Clasificación del Suelo",
    leg_pos = "bottomright"
  )
  mf_layout(
    title = "Subclasificación del Suelo - Santa Cruz de Tenerife",
    credits = "Fuente: SIPU Canarias",
    arrow = FALSE,
    scale = FALSE
  )

  # 5. Guardar y cerrar
  dev.off()
}

# %%
# install.packages("mapsf")
library(mapsf)
library(sf)
suelo_reagrupado_png <- "img/suelo_reagrupado.png"
if (!file.exists(suelo_reagrupado_png)) {
  # 1. Definimos el tema ANTES de exportar
  mf_theme("default")
  # ?mf_export
  # ?png
  # 2. Abrimos el lienzo y le indicamos que use el motor gráfico Cairo
  #debugonce(mf_export)
  class(suelo_reagrupado)
  mf_export(
    x = suelo_reagrupado,
    filename = suelo_reagrupado_png,
    width = 2000,
    res = 300
  )
  # 3. Dibujamos los polígonos
  mf_map(
    x = suelo_reagrupado,
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
}
# %%
# install.packages("maptiles")
library(mapsf)
library(maptiles)
library(sf)

# 1. Definimos el servidor XYZ del PNOA (que contiene los vuelos de IDECanarias)
# l PNOA (Plan Nacional de Ortofotografía Aérea) del IGN de España
url_pnoa <- list(
  name = "PNOA_Ortofoto",
  # src = "https://tms-pnoa-ma.idee.es/1.0.0/pnoa-ma/{z}/{x}/{y}.jpeg",
  url = "https://tms-pnoa-ma.idee.es/1.0.0/pnoa-ma/{z}/{x}/{y}.jpeg",
  q = "",
  # sub = NA,
  cit = "© IGN / GRAFCAN"
)

# 2. Descargamos las teselas ajustadas a la extensión exacta de tu municipio
# Un zoom = 14 o 15 da muy buena resolución. (Cuidado con zoom >= 17, tardará mucho)
debugonce(get_tiles)
ortofoto <- get_tiles(
  x = suelo_reagrupado,
  provider = "Esri.WorldImagery",
  zoom = 14,
  crop = TRUE
)

mapa_santa_cruz_orto_png <- file.path("img/mapa_santa_cruz_orto.png")
unlink(mapa_santa_cruz_orto_png) # Borra el archivo previo si existe, para forzar la regeneración
if (!file.exists(mapa_santa_cruz_orto_png)) {
  print(
    "Archivo no encontrado. Ejecuta el script 'land_class_by_muni.R' para generar el archivo 'mapa_santa_cruz_orto.png' en la carpeta 'img'."
  )

  # 3. Preparamos el tema y el lienzo
  mf_theme("default")
  mf_export(
    x = suelo_reagrupado,
    filename = mapa_santa_cruz_orto_png,
    width = 2000,
    res = 300
  )

  # 4. PASO CLAVE: Dibujamos PRIMERO la ortofoto como fondo
  mf_raster(ortofoto)

  # 5. Dibujamos los polígonos SOBRE la ortofoto
  mf_map(
    x = suelo_reagrupado,
    var = "CLASE_MAIN",
    type = "typo",
    val_order = c("Suelo Urbano", "Suelo Urbanizable", "Suelo Rústico"),
    pal = c("#E31A1C", "#FD8D3C", "#33A02C"),
    border = NA, # Seguimos ocultando los 'slivers' internos
    alpha = 0.6, # <-- IMPORTANTE: 60% de opacidad para dejar ver la ortofoto
    add = TRUE, # <-- IMPORTANTE: add = TRUE le dice que no borre la foto previa
    leg_title = "Clasificación del Suelo",
    leg_pos = "bottomright"
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
}
