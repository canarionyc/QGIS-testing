#%%
library(sf)
library(data.table)

#%% Load data
catastro_dir <- "data/catastro"
# setwd(catastro_dir)
catastro_SC_gpkg <- r"(C:\dev\QGIS-testing\data\catastro\catastro_SC.gpkg)"
print(file.size(catastro_SC_gpkg))
if (!file.exists(catastro_SC_gpkg)) {
  cadastralparcel_gml <- "A.ES.SDGC.CP.38900.cadastralparcel.gml"

  stopifnot(file.exists(cadastralparcel_gml))
  catastro_sf <- st_read(cadastralparcel_gml, quiet = FALSE)
  st_write(catastro_sf, catastro_SC_gpkg, append = FALSE)
  print(file.info(catastro_SC_gpkg))
} else {catastro_sf <- st_read(catastro_SC_gpkg, quiet = FALSE)}
# 1. Fix the missing CRS (EPSG:4083 is REGCAN95 / UTM 28N)
#st_crs(sc_municipality) <- 4083
#st_write(sc_municipality, catastro_shp, append = FALSE)
#%% 2. Convert to data.table

#%% use as data table
str(st_drop_geometry(sc_municipality))
setDT(sc_municipality)

#%% my parcel

my_parcel <- catastro_sf[catastro_sf$nationalCadastralReference == "6295120CS7469N",]
print(st_drop_geometry(my_parcel))
#%% 3. Automated Lookup Function (data.table style)

get_parcel_report <- function(dt, refcat_id) {
  # Subset using data.table's efficient filtering
  parcel <- dt[REFCAT == refcat_id]

  if (nrow(parcel) == 0) {
    stop("REFCAT not found in the dataset.")
  }

  # Basic reporting to console
  cat("\n--- CADASTRAL REPORT ---\n")
  cat("ID (REFCAT): ", parcel$REFCAT, "\n")
  cat("Address:     ", "VIA ", parcel$VIA, " No. ", parcel$NUMERO, "\n")
  cat("Area:        ", parcel$AREA, " m2\n")
  cat("Type:        ", parcel$TIPO, "\n")
  cat("------------------------\n")

  # Base R Spatial Plotting
  # We use st_geometry to ensure we only plot the shape of the specific parcel
  plot(
    st_geometry(parcel),
    col = "khaki",
    border = "red",
    lwd = 2,
    main = paste("Parcel Map:", refcat_id)
  )

  # Add grid or coordinates for context
  axis(1)
  axis(2)
  box()

  return(parcel)
}
# https://www1.sedecatastro.gob.es/Cartografia/mapa.aspx?refcat=6295120CS7469N&from=OVCBusqueda&pest=rc&final=&RCCompleta=6295120CS7469N0001RA&ZV=NO&ZR=NO&anyoZV=&tematicos=&anyotem=&historica=&coordinadas=&del=38&mun=900
refcat_id <- "6295120CS7469N" # Santa Cruz
refcat_id <- "8843707CS4484S0169KT"

# Example Usage:
result <- get_parcel_report(sc_municipality, refcat_id)
