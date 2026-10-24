#%% 1. Import the necessary modules
import json
import xmltodict

#%% 2. Define the path to the XML file
xml_path=r"C:\dev\QGIS-testing\data\Santa Cruz de Tenerife\Plan General de Ordenación de Santa Cruz de Tenerife\fip.xml"

#%% 3. Read the XML file (using the ISO encoding we discovered earlier)
with open(xml_path, 'r', encoding='iso-8859-1') as xml_file:
    # Parse the XML into a Python dictionary
    data_dict = xmltodict.parse(xml_file.read())

#%% 2. Save it as a newly formatted JSON file
json_path=xml_path.replace('.xml', '.json')
with open(json_path, 'w', encoding='utf-8') as json_file:
    # The indent=4 makes it highly readable!
    json.dump(data_dict, json_file, indent=4, ensure_ascii=False)

print("Conversion to JSON complete!")