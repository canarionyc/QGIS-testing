from qgis.utils import iface

# --- CONFIGURATION ---
CODE_FIELD = "ETIPLAN"
TEXT_FIELD = "TXTPLAN"
# ---------------------

layer = iface.activeLayer()

if not layer:
    print("[ERROR] Please click on your layer in the Layers Panel first!")
else:
    renderer = layer.renderer()
    
    # Check if the layer is actually categorized
    if renderer.type() != 'categorizedSymbol':
        print("[ERROR] The layer is not using Categorized symbology. Please set it up in the UI first.")
    else:
        print("Scanning attribute table to build translation dictionary...")
        
        # 1. Build a dictionary mapping the Codes to the Text descriptions
        mapping = {}
        for feat in layer.getFeatures():
            code_val = feat[CODE_FIELD]
            text_val = feat[TEXT_FIELD]
            
            # Ensure we don't map NULL values
            if code_val and text_val:
                mapping[str(code_val)] = str(text_val)
        
        # 2. Loop through the legend categories and update their labels
        categories = renderer.categories()
        updated_count = 0
        
        for i, cat in enumerate(categories):
            code = str(cat.value())
            
            if code in mapping:
                # Update the label (index, new_label_string)
                renderer.updateCategoryLabel(i, mapping[code])
                updated_count += 1
        
        # 3. Refresh the UI to show the changes
        layer.triggerRepaint()
        iface.layerTreeView().refreshLayerSymbology(layer.id())
        
        print(f"[SUCCESS] Updated {updated_count} legend labels to show {TEXT_FIELD}!")