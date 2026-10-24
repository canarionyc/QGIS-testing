def print_tree(group, indent=""):
    for child in group.children():
        if child.nodeType() == QgsLayerTreeNode.NodeGroup:
            print(f"{indent}[GROUP] {child.name()}")
            print_tree(child, indent + "  ")
            
        elif child.nodeType() == QgsLayerTreeNode.NodeLayer:
            layer = child.layer()
            if layer is None:
                continue
                
            print(f"{indent}- [LAYER] {child.name()}")
            
            # Check if it is a Vector Layer to extract Symbology
            if layer.type() == QgsMapLayer.VectorLayer:
                renderer = layer.renderer()
                if renderer:
                    print(f"{indent}  Renderer Type: {renderer.type()}")
                    
                    # If it uses Rule-based symbology
                    if renderer.type() == 'RuleRenderer':
                        root_rule = renderer.rootRule()
                        print(f"{indent}  --- Rules (Drawn Top to Bottom) ---")
                        for idx, rule in enumerate(root_rule.children()):
                            label = rule.label() or "No Label"
                            filter_exp = rule.filterExpression() or "CATCH-ALL (No Filter)"
                            
                            # Extract color if a symbol exists
                            symbol = rule.symbol()
                            if symbol:
                                color = symbol.color().name()
                                type_name = symbol.__class__.__name__
                            else:
                                color = "No Color"
                                type_name = "No Symbol"
                                
                            print(f"{indent}  {idx}. '{label}' | {type_name}: {color} | Filter: {filter_exp}")
                            
                    # If it is just a Single Symbol
                    elif renderer.type() == 'singleSymbol':
                        symbol = renderer.symbol()
                        if symbol:
                            print(f"{indent}  Symbol Color: {symbol.color().name()}")

print("--- WMS LAYER TREE DUMP ---")
root = QgsProject.instance().layerTreeRoot()
print_tree(root)
print("---------------------------")