import os
import csv
from qgis.core import QgsStyle, QgsFillSymbol

print(f"Current Working Directory: {os.getcwd()}")

csv_path = "config/color_ref.csv"
if not os.path.exists(csv_path):
    # Fallback if working directory has not been set to project root
    candidate = os.path.join(r"c:\dev\QGIS-testing", csv_path)
    if os.path.exists(candidate):
        csv_path = candidate
color_dict = {}

# 1. Build the color dictionary from the CSV file
try:
    with open(csv_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            color_dict[row["ETIQPLAN"]] = row["color_hex"]
    print(f"Loaded {len(color_dict)} categories from CSV.")
except Exception as e:
    print(f"[ERROR] Could not read CSV: {e}")

# 2. Access the default QGIS Style Manager
style_manager = QgsStyle.defaultStyle()

OVERWRITE = True  # Set to True to update existing symbols with new colors
added_count = 0
skipped_count = 0

# 3. Loop through the dictionary and create symbols
for category_name, hex_code in color_dict.items():
    if not OVERWRITE and category_name in style_manager.symbolNames():
        print(f"[-] Skipped: '{category_name}' (Already exists in database)")
        skipped_count += 1
        continue

    # Create the symbol
    symbol = QgsFillSymbol.createSimple(
        {"color": hex_code, "outline_color": "black", "outline_width": "0.1"}
    )

    # Add to Style Manager
    success = style_manager.addSymbol(category_name, symbol, OVERWRITE)

    if success:
        print(f"[+] Added/Updated: '{category_name}' with color {hex_code}")
        added_count += 1
    else:
        print(f"[x] Failed to add: '{category_name}'")

# 4. CRITICAL: Save the Style Manager to make it permanent!
if added_count > 0:
    style_manager.save()
    print(
        f"\n[SUCCESS] Permanently saved {added_count} new symbols to the QGIS database!"
    )
else:
    print(f"\n[INFO] No new symbols added to save. {skipped_count} skipped.")
