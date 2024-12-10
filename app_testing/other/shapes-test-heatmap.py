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

# Agregar un mapa de calor basado en la población total
print("Creando mapa de calor...")
folium.Choropleth(
    geo_data=gdf,
    name="Mapa de calor - Población",
    data=gdf,
    columns=["manzana", "pob_tot"],
    key_on="feature.properties.manzana",
    fill_color="YlOrRd",  # Escala de colores amarilla a roja
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Población Total (pob_tot)"
).add_to(m)

# Agregar interacción para mostrar información de cada manzana
print("Agregando interacción...")
for _, row in gdf.iterrows():
    # Crear un popup con información
    popup_info = folium.Popup(
        f"""
        <strong>Manzana:</strong> {row["manzana"]}<br>
        <strong>Población Total (pob_tot):</strong> {row["pob_tot"]}<br>
        <strong>Densidad de Población (dens_pob):</strong> {row["dens_pob"]}
        """,
        max_width=300
    )

    # Agregar una capa para cada geometría con el popup
    folium.GeoJson(
        row["geometry"],
        name=f"Manzana {row['manzana']}",
        tooltip=folium.Tooltip(
            f"Manzana: {row['manzana']}<br>Población Total: {row['pob_tot']}"
        ),
        popup=popup_info,
        style_function=lambda x: {
            'fillColor': 'transparent',
            'color': 'black',
            'weight': 0.5,
            'dashArray': '5, 5'
        }
    ).add_to(m)

# Agregar controles de capas
folium.LayerControl().add_to(m)

# Guardar el mapa como un archivo HTML
output_file = "mapa_interactivo.html"
m.save(output_file)
print(f"Mapa guardado en: {output_file}. Ábrelo en tu navegador.")
