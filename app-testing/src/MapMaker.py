import os
import geopandas as gpd
from shapely.geometry import box
import folium
from branca.colormap import LinearColormap


class MapMaker:
    def __init__(self):
        pass

    def filter_geojson_by_bbox(self, input_geojson_path, bbox):
        """
        Filtra un GeoJSON para incluir solo las geometrías dentro del bounding box y guarda el resultado en 'out'.

        Args:
            input_geojson_path (str): Ruta del archivo GeoJSON de entrada.
            bbox (tuple): Bounding box en formato (lon_min, lat_min, lon_max, lat_max).

        Returns:
            str: Ruta del GeoJSON filtrado.
        """
        # Cargar el archivo GeoJSON
        gdf = gpd.read_file(input_geojson_path)

        # Verificar y configurar CRS si es necesario
        if gdf.crs is None or not gdf.crs.is_geographic:
            gdf.set_crs(epsg=4326, inplace=True)

        # Crear el bounding box como un polígono
        lon_min, lat_min, lon_max, lat_max = bbox
        bbox_polygon = box(lon_min, lat_min, lon_max, lat_max)

        # Filtrar las geometrías que intersectan el bounding box
        filtered_gdf = gdf[gdf.geometry.intersects(bbox_polygon)]

        # Preparar la carpeta y el nombre del archivo de salida
        output_dir = "../out"
        os.makedirs(output_dir, exist_ok=True)  # Crear la carpeta si no existe
        input_filename = os.path.splitext(os.path.basename(input_geojson_path))[0]
        coordinates_suffix = f"-filtered-{lon_min}_{lat_min}_{lon_max}_{lat_max}"
        output_geojson_path = os.path.join(output_dir, f"{input_filename}{coordinates_suffix}.geojson")

        # Guardar el GeoJSON filtrado
        filtered_gdf.to_file(output_geojson_path, driver="GeoJSON")
        return output_geojson_path

    def generate_heatmap(self, input_geojson_path, parameter, output_html_path, title="Mapa de Calor"):
        """
        Genera un mapa de calor basado en un parámetro dado de un GeoJSON.

        Args:
            input_geojson_path (str): Ruta del archivo GeoJSON de entrada.
            parameter (str): Nombre del parámetro a visualizar.
            output_html_path (str): Ruta para guardar el mapa en formato HTML.
            title (str): Título de la leyenda (por defecto: "Mapa de Calor").

        Returns:
            None
        """
        # Cargar el archivo GeoJSON
        gdf = gpd.read_file(input_geojson_path)

        # Verificar si el archivo contiene el parámetro
        if parameter not in gdf.columns:
            raise ValueError(f"El parámetro '{parameter}' no existe en el archivo GeoJSON.")

        # Normalizar los valores del parámetro para el rango de colores
        param_min = gdf[parameter].min()
        param_max = gdf[parameter].max()

        # Crear un mapa centrado en el centroide de las geometrías
        centroid = gdf.geometry.centroid.unary_union.centroid
        center = [centroid.y, centroid.x]
        m = folium.Map(location=center, zoom_start=12)

        # Crear un mapa de colores proporcional
        colormap = LinearColormap(
            colors=["yellow", "orange", "red"], vmin=param_min, vmax=param_max, caption=title
        )

        # Agregar geometrías con colores basados en el parámetro
        for _, row in gdf.iterrows():
            color = colormap(row[parameter])
            popup_info = folium.Popup(
                f"""
                <strong>Información:</strong><br>
                {parameter}: {row[parameter]}<br>
                """,
                max_width=300,
            )
            folium.GeoJson(
                row["geometry"],
                tooltip=folium.Tooltip(f"{parameter}: {row[parameter]}"),
                popup=popup_info,
                style_function=lambda x, color=color: {
                    "fillColor": color,
                    "color": "black",
                    "weight": 0.5,
                    "fillOpacity": 0.7,
                },
            ).add_to(m)

        # Agregar la leyenda y guardar el mapa
        colormap.add_to(m)
        m.save(output_html_path)
