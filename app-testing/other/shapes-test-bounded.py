import os
from dotenv import load_dotenv
import folium
import geopandas as gpd
from shapely.geometry import box
from branca.colormap import LinearColormap

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

# Definir el bounding box
bbox = box(
    -70.69237665060507,  # Longitud de la esquina superior izquierda
    -33.46968475646963,  # Latitud de la esquina inferior derecha
    -70.6258578743538,   # Longitud de la esquina inferior derecha
    -33.43803264216978   # Latitud de la esquina superior izquierda
)

# Filtrar las manzanas dentro del bounding box
gdf = gdf[gdf.geometry.intersects(bbox)]
print(f"Filtradas {len(gdf)} manzanas dentro del bounding box.")

# Crear el mapa centrado en Santiago de Chile
center = [-33.4489, -70.6693]
print(f"Centro del mapa: {center}")
m = folium.Map(location=center, zoom_start=14)

# Normalizar los valores de población para el rango de colores
pob_min = gdf["pob_tot"].min()
pob_max = gdf["pob_tot"].max()
print(f"Normalizando colores: pob_min={pob_min}, pob_max={pob_max}")

# Crear un mapa de colores proporcional
colormap = LinearColormap(
    colors=["yellow", "orange", "red"],  # Colores de menor a mayor
    vmin=pob_min,
    vmax=pob_max,
    caption="Población Total (pob_tot)"
)

# Agregar geometrías con colores basados en la población
for _, row in gdf.iterrows():
    # Calcular el color proporcional
    color = colormap(row["pob_tot"])

    # Crear un popup con información
    popup_info = folium.Popup(
        f"""
        <strong>Manzana:</strong> {row["manzana"]}<br>
        <strong>Población Total (pob_tot):</strong> {row["pob_tot"]}<br>
        <strong>Densidad de Población (dens_pob):</strong> {row["dens_pob"]}
        """,
        max_width=300
    )

    # Agregar cada manzana al mapa con el color calculado
    folium.GeoJson(
        row["geometry"],
        name=f"Manzana {row['manzana']}",
        tooltip=folium.Tooltip(
            f"Manzana: {row['manzana']}<br>Población Total: {row['pob_tot']}"
        ),
        popup=popup_info,
        style_function=lambda x, color=color: {
            'fillColor': color,
            'color': 'black',
            'weight': 0.5,
            'fillOpacity': 0.7
        }
    ).add_to(m)

# Agregar el mapa de colores al mapa
colormap.add_to(m)

# Agregar controles de capas
folium.LayerControl().add_to(m)

# Guardar el mapa como un archivo HTML
output_file = "mapa_filtrado.html"
m.save(output_file)
print(f"Mapa guardado en: {output_file}. Ábrelo en tu navegador.")
