canvas = iface.mapCanvas()
point = canvas.center()

print(f"--- WMS QUERY AT MAP CENTER ---")
print(f"Coordinates: X={point.x():.2f}, Y={point.y():.2f}\n")

# These are the two exact FIP Fusión layers we found in your dump
target_layers = ['Categoría y subcategoría del suelo', 'Clasificación de suelo']

for layer in QgsProject.instance().mapLayers().values():
    if layer.name() in target_layers:
        print(f">> RESULTS FOR: {layer.name().upper()}")
        try:
            # Triggering the WMS GetFeatureInfo request programmatically
            ident = layer.dataProvider().identify(
                point, 
                QgsRaster.IdentifyFormatFeature, 
                canvas.extent(), 
                canvas.width(), 
                canvas.height()
            )
            
            if ident.isValid() and ident.features():
                for feat in ident.features():
                    for attr_name, attr_value in feat.attributes().items():
                        # Filtering out empty HTML tags or nulls for clean reading
                        if attr_value and str(attr_value).strip() != "":
                            print(f"  {attr_name}: {attr_value}")
            else:
                print("  [No data found at this exact point]")
        except Exception as e:
            print(f"  [Error querying layer: {e}]")
        print("-" * 40)