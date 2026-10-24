#%% Desglose Santa Cruz de Tenerife
#library(sf)
# library(dplyr)

# # 2. Calculamos las áreas y agrupamos
# desglose_santa_cruz <- suelo %>%
#   # st_area() calcula el área exacta en base al CRS (en este caso, m2)
#   mutate(
#     area_m2 = as.numeric(st_area(geometry)),
#     area_ha = area_m2 / 10000
#   ) %>%
#   # Agrupamos por la columna que tiene el nombre del suelo
#   group_by(TXTPLAN) %>%
#   # Sumamos todas las hectáreas de la misma clase y quitamos la geometría para ver la tabla limpia
#   summarise(total_ha = round(sum(area_ha), 2)) %>%
#   # st_drop_geometry() %>% 
#   # Calculamos el porcentaje relativo
#   mutate(
#     porcentaje = round((total_ha / sum(total_ha)) * 100, 2)
#   ) %>%
#   # Ordenamos de mayor a menor
#   arrange(desc(total_ha))


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