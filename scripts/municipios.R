
library(sf)
# %% municipios

# Notice the /vsizip/ at the very beginning and the use of forward slashes
municipios <- st_read("/vsizip/C:/dev/QGIS-testing/data/gobcan_unidades-administrativas_municipios.zip")
#municipios <- st_transform(municipios, 32628)
municipios <- st_make_valid(municipios)
print(st_drop_geometry(municipios))