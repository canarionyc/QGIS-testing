# %% [IMPORTACIONES Y CONFIGURACIÓN / IMPORTS AND CONFIGURATION]
import json
import pandas as pd

# %% [CONFIGURACIÓN DE IDIOMA / LANGUAGE CONFIGURATION]
# Toggle switch for terminal outputs
LANG = "ES"

messages = {
    "EN": {
        "no_data": "No data loaded. Please run load_json() first.",
        "success": "Spreadsheet successfully generated at: ",
        "processing": "Processing bridge: ",
    },
    "ES": {
        "no_data": "No hay datos cargados. Ejecute load_json() primero.",
        "success": "Hoja de cálculo generada con éxito en: ",
        "processing": "Procesando puente: ",
    },
}


# %% [CLASE CONVERSORA / CONVERTER CLASS]
class JsonToSheetsConverter:
    """
    ES: Clase para convertir el JSON de puentes a un formato multipestaña para Google Sheets.
    EN: Class to convert the bridges JSON into a multi-tab format for Google Sheets.
    """

    def __init__(self, input_path: str, output_path: str):
        self.input_path = input_path
        self.output_path = output_path
        self.data = None

    def load_json(self):
        with open(self.input_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def generate_spreadsheet(self):
        """
        ES: Aplana los 'hallazgos' y crea una hoja por cada 'puente'.
        EN: Flattens the 'hallazgos' and creates one sheet per 'puente'.
        """
        if not self.data:
            print(messages[LANG]["no_data"])
            return

        # Requires 'openpyxl' installed (pip install openpyxl)
        with pd.ExcelWriter(self.output_path, engine="openpyxl") as writer:
            for item in self.data:
                # 1. Clean Sheet Naming (Max 31 chars for Google Sheets)
                raw_name = item.get("puente", "Unknown_Bridge")
                clean_name = raw_name.split("_")[0][:31]

                print(f"{messages[LANG]['processing']} {clean_name}")

                # 2. Flatten Data structure
                hallazgos = item.get("hallazgos", [])
                rows = []
                for h in hallazgos:
                    # Start with the main 'capa'
                    row = {"Capa_Principal": h.get("capa", "")}

                    # Merge all nested dictionary items from 'datos' into the row
                    datos = h.get("datos", {})
                    row.update(datos)

                    rows.append(row)

                # 3. Write to the specific tab
                df = pd.DataFrame(rows)
                df.to_excel(writer, sheet_name=clean_name, index=False)

        print(f"\n{messages[LANG]['success']}{self.output_path}")


# %% [DEMOSTRACIÓN DE FUNCIONALIDAD / FUNCTIONALITY DEMONSTRATION]
if __name__ == "__main__":
    # ES: Parámetros de entrada y salida
    # EN: Input and output parameters
    input_file = r"C:\dev\QGIS-testing\resultados_puentes_final.json"
    output_file = "Puentes_Google_Sheets.xlsx"

    # ES: Instanciar y ejecutar la clase
    # EN: Instantiate and run the class
    converter = JsonToSheetsConverter(input_file, output_file)
    converter.load_json()
    converter.generate_spreadsheet()
