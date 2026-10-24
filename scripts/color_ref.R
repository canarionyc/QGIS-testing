# %%
if(file.exists("data/color_ref.csv")) {
    color_ref <- read.csv("data/color_ref.csv")
  color_mapping <- setNames(color_ref$color_hex, color_ref$ETIQUETA)
  color_mapping
} else {
  # %% Create a reference dataframe with your exact hex codes
  color_ref <- data.frame(
    ETIQUETA = c(
      "SUC",
      "SUNC",
      "SUC-IC",

      "SUS",
      "SUSNO",
      "SUNS",
      "SUNS-E",
      "SUNS-D",
      "SUSO",

      "SRPP",
      "SRPN",
      "SRPI",
      "SRPA",
      "SRPM",
      "SRAR",
      "SRPT-2",
      "SRPT-1",

      "SRPL",
      "SRPH"
    ),
    color_hex = c(
      "#990000",
      "#CC3333",
      "#FF9999",

      "#CC6600",
      "#E68000",
      "#FF9933",
      "#FFB266",
      "#FFCC99",
      "#FFE5CC",

      "#004D00",
      "#006600",
      "#008000",
      "#339933",
      "#66B266",
      "#99CC99",
      "#CCE5CC",
      "#E5F2E5",

      "#00008B",
      "#ADD8E6"
    )
  )

  write.csv(color_ref, "data/color_ref.csv", row.names = FALSE)

}

# %% 1. Define the categories by ETIQUETA
urbano <- c("SUC", "SUNC", "SUC-IC") # 3 classes
urbanizable <- c("SUS", "SUSNO", "SUNS", "SUNS-E", "SUNS-D", "SUSO") # 6 classes
rustico <- c(
  "SRPP",
  "SRPN",
  "SRPI",
  "SRPA",
  "SRPL",
  "SRPM",
  "SRAR",
  "SRPT-2",
  "SRPH",
  "SRPT-1"
) # 10 classes

# 2. Generate specific color ramps
# (Interpolating from light to dark to ensure distinguishability)
pal_urbano <- colorRampPalette(c("#FF9999", "#990000"))(length(urbano))
pal_urbanizable <- colorRampPalette(c("#FFCC99", "#CC6600"))(length(
  urbanizable
))
pal_rustico <- colorRampPalette(c("#CCFFCC", "#004D00"))(length(rustico))

color_mapping <- c(
  setNames(pal_urbano, urbano),
  setNames(pal_urbanizable, urbanizable),
  setNames(pal_rustico, rustico)
)