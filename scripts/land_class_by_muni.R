# %% ANÁLISIS DE CLASES DE SUELO POR MUNICIPIO EN CANARIAS
library(data.table)

library(sf)
# sf::as_Spatial(FALSE)
# source("scripts/color_ref.R")
print(getwd())
print(.libPaths())

# %% suelo agrupadoSanta Cruz de Tenerife
unlink("data/suelo_agrupado.gpkg")
if (!file.exists("data/suelo_agrupado.gpkg")) {
  # install.packages("data.table")

  suelo <- st_read(
    dsn = r"(C:\dev\QGIS-testing\data\140613-pgo-sct-sipu\02SIST\CLA.shp)",
    stringsAsFactors = TRUE,
    options = "ENCODING=UTF-8"
  )
  # suelo <- st_transform(suelo, 32628)
  suelo <- st_make_valid(suelo)
  st_drop_geometry(suelo) |> summary() |> print()


  # 1. Aseguramos que sea un data.table
  setDT(suelo)
  suelo[, .N, keyby = .(ETIPLAN)]
  
  suelo["ETIQUETA" %in% c("SRPT-2", "SRPT-1" ),]
  # suelo <- suelo[!is.na(ETIPLAN)  & ! ETIPLAN %in% c('SUS'), ]
  
  suelo[, area_m2 := round(as.numeric(st_area(geometry)))]
  suelo[, area_ha := round(area_m2 / 10000, 2)]
  # 2. Agregación con el ejemplar mayor y disolución espacial
  suelo_agrupado <- suelo[,
    .(
      area_ha = sum(area_ha, na.rm = TRUE),

      # Extraemos el nombre (o etiqueta) del polígono más grande del grupo
      ejmplr_m_c = CODIGO[which.max(area_ha)],

      # Si prefieres el texto descriptivo, usa:
      ejmplr_m_h = area_ha[which.max(area_ha)],

      # Disolución espacial (une todos los polígonos del grupo en uno solo)
      # geometry = st_union(geometry)
      geometry = st_union(st_buffer(geometry, dist = 0.01))
    ),
    by = .(ETIPLAN, TXTPLAN)
  ]
  suelo_agrupado |> summary() |> print()

  setorderv(suelo_agrupado, "area_ha", order = -1L)

  # str(suelo_agrupado)

  suelo_agrupado[,
    CLASE_MAIN := fcase(
      grepl("Urbano", TXTPLAN)      , "Suelo Urbano"      ,
      grepl("Urbanizable", TXTPLAN) , "Suelo Urbanizable" ,
      grepl("Rústico", TXTPLAN)     , "Suelo Rústico"     ,
      default = "Otros / Sistemas Generales"
    ) |>
      as.factor()
  ]
  
  suelo_agrupado |> summary() |> print()

  #str(suelo_agrupado)
  # %% merge con color_ref para asignar colores
  suelo_agrupado <- merge(
    suelo_agrupado,
    color_ref,
    by = "ETIQUETA",
    all.x = TRUE
  )

  suelo_agrupado <- st_as_sf(suelo_agrupado)
  st_write(suelo_agrupado, "data/suelo_agrupado.gpkg", append = FALSE)
} else {
  suelo_agrupado <- st_read("data/suelo_agrupado.gpkg", stringsAsFactors = TRUE)
}
str()
suelo_agrupado |> summary() |> print()

suelo_agrupado <- st_drop_geometry(suelo_agrupado) |> as.data.table() |> setDT(suelo_agrupado)
suelo_agrupado[, "color_hex":=NULL]
suelo_agrupado |> fwrite( "data/suelo_agrupado.csv")

suelo_agrupado[, c(
  "ETIQUETA",
  "TXTPLAN"
  #, "area_ha", "CLASE_MAIN"
)] |> st_drop_geometry()


#%% make legend colors

# %% agrupar by main class
if (!file.exists("data/suelo_reagrupado.gpkg")) {
  print(
    "Archivo no encontrado. Ejecuta el script 'land_class_by_muni.R' para generar el archivo 'suelo_reagrupado.gpkg' en la carpeta 'data'."
  )

  suelo_reagrupado <- suelo_agrupado[,
    .(
      area_ha = sum(area_ha, na.rm = TRUE),

      # Extraemos el nombre (o etiqueta) del polígono más grande del grupo
      ejmplr_m_c = ejmplr_m_c[which.max(area_ha)],

      # Si prefieres el texto descriptivo, usa:
      ejmplr_m_h = area_ha[which.max(area_ha)],

      # Disolución espacial (une todos los polígonos del grupo en uno solo)
      # geometry = st_union(geometry)
      geometry = st_union(st_buffer(geometry, dist = 0.01))
    ),
    by = .(CLASE_MAIN)
  ]
  print(suelo_reagrupado)

  setorderv(suelo_reagrupado, "area_ha", order = -1L)

  print(suelo_reagrupado)

  # %% Luego guardas el shapefile con st_write()
  # Ver el resultado
  # 3. Restauramos la clase sf para poder mapear o exportar
  suelo_reagrupado <- st_as_sf(suelo_reagrupado)

  str(suelo_reagrupado)
  # st_write(suelo_reagrupado, "data/suelo_reagrupado.shp", append = FALSE, delete_layer = TRUE)
  # saveRDS(suelo_reagrupado, "data/desglose_santa_cruz.rds")

  # El estándar moderno: un solo archivo, sin límites de caracteres, a prueba de balas
  st_write(
    suelo_reagrupado,
    "data/suelo_reagrupado.gpkg",
    delete_dsn = TRUE # Borra el archivo previo si existe
  )
} else {
  suelo_reagrupado <- st_read("data/suelo_reagrupado.gpkg")
  print(suelo_reagrupado)
}
