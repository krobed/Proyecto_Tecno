import os
from dotenv import load_dotenv
import folium
import geopandas as gpd

# Cargar variables desde el archivo .env
load_dotenv()

# Obtener el path del archivo GeoJSON desde la variable de entorno
geojson_path = os.getenv("GEOJSON_PATH_POBLACION")

if not geojson_path:
    raise ValueError("La ruta del archivo GeoJSON no está definida en el archivo .env")

# Cargar el archivo GeoJSON
print("Cargando archivo GeoJSON...")
gdf = gpd.read_file(geojson_path)

# Verificar si el archivo tiene geometrías
if gdf.empty:
    raise ValueError("El archivo GeoJSON no contiene datos.")

# Asegurarse de que el CRS es EPSG:4326
if gdf.crs is None or not gdf.crs.is_geographic:
    print("Configurando CRS como EPSG:4326...")
    gdf.set_crs(epsg=4326, inplace=True)

# Crear el mapa centrado en Santiago de Chile
center = [-33.4489, -70.6693]
print(f"Centro del mapa: {center}")
m = folium.Map(location=center, zoom_start=12)

# Agregar GeoJSON al mapa
print("Agregando geometrías al mapa...")
folium.GeoJson(
    gdf,
    name="Predios Santiago",
    style_function=lambda x: {
        'fillColor': 'blue',
        'color': 'black',
        'weight': 0.5,
        'fillOpacity': 0.4
    }
).add_to(m)

# Agregar controles de capas
folium.LayerControl().add_to(m)

print("Mapa generado. Renderizando...")
m
