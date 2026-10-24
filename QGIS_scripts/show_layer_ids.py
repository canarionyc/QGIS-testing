# No need to import QGIS, 'iface' is globally available in the QGIS console
print(f"{'Index':<6} | {'ID String':<30} | {'Layer Name'}")
print("-" * 60)

# We use the layer tree to get the current order
layers = iface.mapCanvas().layers()

for i, layer in enumerate(layers):
    # .id() returns the long unique string
    # i is the current index (could be your '99')
    print(f"{i:<6} | {layer.id()[:30]:<30} | {layer.name()}")