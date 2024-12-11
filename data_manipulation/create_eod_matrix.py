import pandas as pd

# Cargar el archivo CSV (asegúrate de reemplazar 'archivo.csv' con la ruta correcta de tu archivo)
input_file = r"C:\Users\pablo\Escritorio\EL6101-Proyecto_Tecno\data\tablasWeb2018Oct_08_12.MatrizODComunasMediaHora.csv"
output_file = "Matriz_OD_Diaria_COMUNAL_2018.csv"

# Leer el archivo CSV con el delimitador correcto (';')
data = pd.read_csv(input_file, delimiter=';')

# Imprimir las columnas disponibles para verificar nombres
print("Columnas disponibles en el archivo:", data.columns.tolist())

# Seleccionar las columnas necesarias (asumiendo que las columnas de "viajes" tienen un prefijo conocido como 'Viaje')
columns_viajes = [col for col in data.columns if col.startswith("Viaje")]
columns_to_group = ["ComunaSubida", "ComunaBajada"]

# Verificar si las columnas necesarias existen en el archivo
missing_columns = [col for col in columns_to_group if col not in data.columns]
if missing_columns:
    raise KeyError(f"Las siguientes columnas no se encuentran en el archivo: {missing_columns}")

# Asegurar que sólo las columnas necesarias estén en el DataFrame
data_filtered = data[columns_to_group + columns_viajes]

# Agrupar por ComunaSubida y ComunaBajada, y sumar las columnas de viajes
result = data_filtered.groupby(["ComunaSubida", "ComunaBajada"], as_index=False).sum()

# Renombrar las columnas sumadas para reflejar "suma_" como prefijo
result = result.rename(columns={col: f"suma_{col}" for col in columns_viajes})

# Guardar el resultado en un nuevo archivo CSV
result.to_csv(output_file, index=False)

print(f"Archivo generado exitosamente: {output_file}")
