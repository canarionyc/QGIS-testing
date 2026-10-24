import xml.etree.ElementTree as ET
import pandas as pd
import csv
from pathlib import Path

# --- CONFIGURACIÓN ---
# ¡IMPORTANTE! Cambia esta ruta a donde tengas tu archivo XML de 86MB
xml_file = r'C:\dev\QGIS-testing\data\Categorias_FIP_SantaCruz\fip.xml'
csv_file = r'C:\dev\QGIS-testing\data\Categorias_FIP_SantaCruz.csv'

print("--- FIP XML PARSER AVANZADO Y CORRECCIÓN DE MOJIBAKE ---")

data = []


# Función mágica para arreglar el error del Gobierno de Canarias
def fix_mojibake(text):
    if not text:
        return ""
    try:
        # Revertimos la mala lectura Latin-1 y la decodificamos bien como UTF-8
        return text.encode('latin1').decode('utf-8')
    except:
        return text


try:
    # Leemos el XML (ignorando su falso encabezado)
    context = ET.iterparse(xml_file, events=('end',))

    for event, elem in context:
        tag_name = elem.tag.split('}')[-1]

        # Extraemos las etiquetas donde el FIP guarda la "chicha" legal
        if tag_name in ['NOMBRE', 'TEXTO', 'NOMBRE_DETERMINACION', 'CLAVE']:
            if elem.text and elem.text.strip():
                texto_original = elem.text.strip()

                # Filtramos para quedarnos con urbanismo
                if any(kw in texto_original.upper() for kw in ['SUELO', 'CATEGOR', 'URBAN', 'RÚSTIC']):
                    texto_arreglado = fix_mojibake(texto_original)

                    # Lo guardamos como diccionario para hacer un buen CSV de varias columnas
                    data.append({
                        'Etiqueta_XML': tag_name,
                        'Texto_Extraido': texto_arreglado
                    })

        # Liberar memoria
        elem.clear()

    # Convertir a DataFrame de Pandas para manejarlo fácilmente y quitar duplicados
    df = pd.DataFrame(data).drop_duplicates()

    # Guardar en CSV con utf-8-sig para que Excel lo abra perfecto a la primera
    df.to_csv(csv_file, index=False, encoding='utf-8-sig', sep='|')

    print(f"\n¡Éxito! Se extrajeron {len(df)} filas bien estructuradas.")
    print(f"Archivo guardado en: {csv_file}")

    print("\n--- MUESTRA RÁPIDA DE LA EXTRACCIÓN (Primeras 3) ---")
    for index, row in df.head(3).iterrows():
        print(f"[{row['Etiqueta_XML']}] -> {row['Texto_Extraido'][:80]}...")

except Exception as e:
    print(f"Error al analizar el XML: {e}")