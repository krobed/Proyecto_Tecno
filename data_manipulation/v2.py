import pandas as pd
import geopandas as gpd
from unidecode import unidecode
import folium

# Archivos de entrada
csv_file = "Matriz_OD_Diaria_COMUNAL_2018.csv"
geojson_file = "ComunasRM.geojson"
output_geojson_file = "Filtered_ComunasRM.geojson"
output_csv_file = "Updated_Matriz_OD_Diaria_COMUNAL_2018.csv"
map_output_file = "Filtered_ComunasRM_Map.html"

# Cargar el archivo CSV
data_csv = pd.read_csv(csv_file, delimiter=',')

# Extraer las comunas únicas del archivo CSV y normalizarlas
csv_comunas = data_csv['ComunaSubida'].dropna().unique().tolist() + data_csv['ComunaBajada'].dropna().unique().tolist()
csv_comunas = set(unidecode(comuna.strip().upper()) for comuna in csv_comunas)

# Cargar el archivo GeoJSON
data_geojson = gpd.read_file(geojson_file)

# Filtrar las comunas del GeoJSON que están en el CSV
def normalize_comuna(comuna):
    return unidecode(comuna.strip().upper())

data_geojson['NormalizedComuna'] = data_geojson['Comuna'].apply(normalize_comuna)
filtered_geojson = data_geojson[data_geojson['NormalizedComuna'].isin(csv_comunas)]

# Crear un diccionario para mapear nombres de comunas a sus OBJECTID
comuna_to_objectid = filtered_geojson.set_index('NormalizedComuna')['objectid'].to_dict()

# Agregar columnas id_comuna_origen y id_comuna_destino al CSV original
data_csv['NormalizedComunaSubida'] = data_csv['ComunaSubida'].apply(lambda x: unidecode(str(x).strip().upper()))
data_csv['NormalizedComunaBajada'] = data_csv['ComunaBajada'].apply(lambda x: unidecode(str(x).strip().upper()))

data_csv['id_comuna_origen'] = data_csv['NormalizedComunaSubida'].map(comuna_to_objectid)
data_csv['id_comuna_destino'] = data_csv['NormalizedComunaBajada'].map(comuna_to_objectid)

# Eliminar columnas normalizadas temporales
data_csv = data_csv.drop(columns=['NormalizedComunaSubida', 'NormalizedComunaBajada'])

# Guardar el nuevo CSV con las columnas de ID
data_csv.to_csv(output_csv_file, index=False, sep=',')

# Eliminar la columna de normalización antes de guardar el GeoJSON
filtered_geojson = filtered_geojson.drop(columns=['NormalizedComuna'])
filtered_geojson.to_file(output_geojson_file, driver='GeoJSON')

# Visualizar el GeoJSON filtrado en un mapa interactivo
center = [filtered_geojson.geometry.centroid.y.mean(), filtered_geojson.geometry.centroid.x.mean()]
mapa = folium.Map(location=center, zoom_start=11)
folium.GeoJson(filtered_geojson).add_to(mapa)

# Guardar el mapa como un archivo HTML
mapa.save(map_output_file)

print(f"Archivo GeoJSON filtrado guardado como: {output_geojson_file}")
print(f"Archivo CSV actualizado guardado como: {output_csv_file}")
print(f"Mapa interactivo guardado como: {map_output_file}")