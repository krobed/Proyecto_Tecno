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

# Medir el tiempo de carga
print("Cargando archivo GeoJSON...")
gdf = gpd.read_file(geojson_path)

# Reproyectar solo si es necesario
if gdf.crs is None or gdf.crs.is_geographic:
    print("Reproyectando geometrías a EPSG:3857...")
    gdf = gdf.to_crs(epsg=3857)

# Simplificar geometrías para acelerar visualización
print("Simplificando geometrías...")
gdf['geometry'] = gdf['geometry'].simplify(tolerance=10)  # Ajusta el valor según tu necesidad

# Obtener el centro del mapa para inicializar
center = [gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()]

# Crear el mapa interactivo con Folium
print("Generando mapa interactivo...")
m = folium.Map(location=center, zoom_start=13)

# Convertir geometrías a CRS EPSG:4326 para Folium y agregar al mapa
folium.GeoJson(
    gdf.to_crs(epsg=4326),  # Convertir de nuevo a EPSG:4326 para la visualización
    name="Simplified GeoJSON",
    style_function=lambda x: {
        'fillColor': 'blue',
        'color': 'black',
        'weight': 0.5,
        'fillOpacity': 0.4
    }
).add_to(m)

# Agregar controles al mapa
folium.LayerControl().add_to(m)

print("Mapa generado. Renderizando...")
# Mostrar el mapa
m
