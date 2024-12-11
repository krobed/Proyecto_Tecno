import pandas as pd
import geopandas as gpd

# Archivos de entrada
csv_file = "Updated_Matriz_OD_Diaria_COMUNAL_2018.csv"
geojson_file = "Filtered_ComunasRM.geojson"
output_geojson_file = "GeoJSON_With_Viajes.geojson"

# Cargar el archivo CSV
data_csv = pd.read_csv(csv_file, delimiter=',')

# Cargar el archivo GeoJSON
data_geojson = gpd.read_file(geojson_file)

# Crear un diccionario para almacenar los valores de "suma_ViajeLaboralPromedio" agrupados por origen y destino
viajes_dict = {}
for _, row in data_csv.iterrows():
    origen_id = int(row['id_comuna_origen'])
    destino_id = int(row['id_comuna_destino'])
    suma_viajes = row['suma_ViajeLaboralPromedio']

    if origen_id not in viajes_dict:
        viajes_dict[origen_id] = {}
    viajes_dict[origen_id][destino_id] = suma_viajes

# Agregar las propiedades al GeoJSON
for idx, row in data_geojson.iterrows():
    comuna_id = int(row['objectid'])

    # Verificar si hay datos de viajes laborales desde esta comuna origen
    if comuna_id in viajes_dict:
        destinos = viajes_dict[comuna_id]
        for destino_id, suma_viajes in destinos.items():
            property_name = f"viajesDiariosDestino_{destino_id}"
            data_geojson.at[idx, property_name] = suma_viajes

# Guardar el nuevo GeoJSON con las propiedades adicionales
data_geojson.to_file(output_geojson_file, driver='GeoJSON')

print(f"Archivo GeoJSON actualizado guardado como: {output_geojson_file}")