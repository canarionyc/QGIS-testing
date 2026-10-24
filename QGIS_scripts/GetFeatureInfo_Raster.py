canvas = iface.mapCanvas()
point = canvas.center()

print(f"--- WMS QUERY AT MAP CENTER ---")
print(f"Coordinates: X={point.x():.2f}, Y={point.y():.2f}\n")

target_layers = ['Categoría y subcategoría del suelo', 'Clasificación de suelo']

for layer in QgsProject.instance().mapLayers().values():
    if layer.name() in target_layers:
        print(f">> RESULTS FOR: {layer.name().upper()}")
        try:
            ident = layer.dataProvider().identify(
                point, 
                QgsRaster.IdentifyFormatFeature, 
                canvas.extent(), 
                canvas.width(), 
                canvas.height()
            )
            
            if ident.isValid() and ident.results():
                # En WMS, results() devuelve un diccionario
                for band, data in ident.results().items():
                    if isinstance(data, list):  # Normalmente es una lista de QgsFeature
                        for feat in data:
                            # Iteramos por los campos del feature
                            for field in feat.fields():
                                attr_name = field.name()
                                attr_value = feat[attr_name]
                                if attr_value and str(attr_value).strip() != "":
                                    print(f"  {attr_name}: {attr_value}")
                    elif isinstance(data, dict):
                        for k, v in data.items():
                            print(f"  {k}: {v}")
                    else:
                        print(f"  Raw Data: {data}")
            else:
                print("  [No data found at this exact point]")
        except Exception as e:
            print(f"  [Error querying layer: {e}]")
        print("-" * 40)