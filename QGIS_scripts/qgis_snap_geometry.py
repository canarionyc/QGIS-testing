# Use runAndLoadResults so it actually appears in your Layers Panel
processing.runAndLoadResults("native:snapgeometries", {
    'INPUT': 'C:/dev/PteZurita/GrafCan/Markings_4083.shp',
    'REFERENCE_LAYER': 'C:/dev/PteZurita/GrafCan/Markings_4083.shp',
    'TOLERANCE': 0.05,  # Increased slightly to be safe
    'BEHAVIOR': 2,      # 2 = Prefer closest point on line (CRITICAL)
    'OUTPUT': 'memory:Snapped_Markings'
})