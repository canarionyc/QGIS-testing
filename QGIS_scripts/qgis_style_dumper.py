from qgis.core import QgsStyle

# Get the default style manager
style = QgsStyle.defaultStyle()
all_symbols = style.symbolNames()

# The list of your categories
my_categories = [
    "SUCO", "SUNC", "SUC-IC", "SUS", "SUSNO", "SUNS", "SUNSE", "SUNSD", "SUSO", 
    "SRPP", "SRPN", "SRPI", "SRPA", "SRPM", "SRAR", "SRPT-AT", "SRPT-AL", 
    "SRPL", "SRPH"
]

print("--- Checking QGIS Default Style Database ---")
print(f"Total symbols found in database: {len(all_symbols)}")
print("-" * 40)

found_count = 0

for cat in my_categories:
    if cat in all_symbols:
        # Fetch the actual symbol object
        sym = style.symbol(cat)
        if sym:
            # sym.type() returns 2 for Fill (Polygon) symbols
            print(f"✅ FOUND: {cat} (Type: {sym.type()}, Color: {sym.color().name()})")
        else:
            print(f"⚠️ NAME IN DB BUT SYMBOL IS NULL: {cat}")
        found_count += 1
    else:
        print(f"❌ MISSING: {cat}")

print("-" * 40)
print(f"Summary: Found {found_count} out of {len(my_categories)} targets.")