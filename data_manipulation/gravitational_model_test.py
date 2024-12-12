import visualization_app

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from turfpy.transformation import circle
from geojson import Point as GeoJsonPoint

# Parámetro para habilitar o deshabilitar la depuración de círculos de influencia
debug_shapes = False


def apply_multiple_gravitational_characteristic_models(buildings: list, input_geojson: str,
                                                       caracterizacion_comunas: dict) -> str:
    # Cargar el GeoJSON inicial
    data_geojson = gpd.read_file(input_geojson)

    # Validar la presencia de 'objectid'
    if 'objectid' not in data_geojson.columns:
        raise ValueError("El archivo GeoJSON no contiene la columna 'objectid'.")

    # Lista para almacenar los círculos de influencia si debug_shapes está habilitado
    influence_circles = [] if debug_shapes else None

    # Iterar sobre cada building y aplicar las transformaciones acumulativamente
    for building in buildings:
        coords = building['coords']
        local_effect_radius = building['local_effect_radius']
        gravity_constant = building['gravity_constant']
        global_multiplier = building['global_multiplier']
        multiplier_group, multiplier_value = global_multiplier

        # Crear un círculo de influencia utilizando Turfpy
        center = GeoJsonPoint((coords[1], coords[0]))  # Turfpy usa coordenadas (lon, lat)
        circle_geojson = circle(
            center,
            radius=local_effect_radius / 1000,  # Convertir metros a kilómetros
            units="km"
        )

        influence_circle = gpd.GeoDataFrame.from_features([circle_geojson])
        influence_circle.set_crs("EPSG:4326", inplace=True)

        if debug_shapes:
            influence_circles.append(influence_circle.geometry.iloc[0])

        # Detectar comunas que intersectan con el círculo
        intersecting_comunas = data_geojson[data_geojson.geometry.intersects(influence_circle.geometry.iloc[0])]

        if intersecting_comunas.empty:
            print(f"No se encontraron comunas dentro del radio de influencia para el building en {coords}.")
            continue

        # Obtener los IDs de las comunas intersectadas
        intersecting_ids = intersecting_comunas['objectid'].tolist()

        # Modificar las propiedades de viajes acumulativamente
        def modify_travel_values(row):
            for key in row.index:
                if key.startswith('viajesDiariosDestino_'):
                    destino_id = int(key.split('_')[-1])
                    if destino_id in intersecting_ids:
                        comuna_name = row['Comuna'] if 'Comuna' in row else None

                        # Verificar si la comuna está en el diccionario de caracterización
                        if comuna_name in caracterizacion_comunas:
                            comuna_group = caracterizacion_comunas[comuna_name]

                            # Aplicar el global_multiplier si coincide el grupo
                            if comuna_group == multiplier_group:
                                row[key] *= multiplier_value
                            else:
                                row[key] *= gravity_constant
                        else:
                            # Aplicar gravity_constant si no está en el diccionario
                            row[key] *= gravity_constant
            return row

        data_geojson = data_geojson.apply(modify_travel_values, axis=1)

    if debug_shapes:
        # Crear un GeoDataFrame para los círculos de influencia
        circles_gdf = gpd.GeoDataFrame(geometry=influence_circles, crs="EPSG:4326")

        # Combinar el GeoDataFrame original con los círculos de influencia
        combined_gdf = pd.concat([data_geojson, circles_gdf], ignore_index=True)

        # Guardar el nuevo archivo GeoJSON con círculos de influencia
        output_geojson = input_geojson.replace('.geojson', '_modified_with_circles.geojson')
        combined_gdf.to_file(output_geojson, driver='GeoJSON')
    else:
        # Guardar el nuevo archivo GeoJSON sin círculos de influencia
        output_geojson = input_geojson.replace('.geojson', '_modified.geojson')
        data_geojson.to_file(output_geojson, driver='GeoJSON')

    print(f"Archivo modificado guardado como {output_geojson}")
    return output_geojson


def apply_multiple_gravitational_models(buildings: list, input_geojson: str) -> str:
    # Crear un archivo temporal para las modificaciones acumulativas
    temp_geojson = "temp.geojson"
    data_geojson = gpd.read_file(input_geojson)
    data_geojson.to_file(temp_geojson, driver="GeoJSON")

    # Iterar sobre cada building y aplicar las transformaciones acumulativamente
    for building in buildings:
        data_geojson = gpd.read_file(temp_geojson)  # Leer el archivo temporal

        coords = building['coords']
        local_effect_radius = building['local_effect_radius']
        gravity_constant = building['gravity_constant']

        # Crear un círculo de influencia utilizando Turfpy
        center = GeoJsonPoint((coords[1], coords[0]))  # Turfpy usa coordenadas (lon, lat)
        circle_geojson = circle(
            center,
            radius=local_effect_radius / 1000,  # Convertir metros a kilómetros
            units="km"
        )

        influence_circle = gpd.GeoDataFrame.from_features([circle_geojson])
        influence_circle.set_crs("EPSG:4326", inplace=True)

        # Detectar comunas que intersectan con el círculo
        intersecting_comunas = data_geojson[data_geojson.geometry.intersects(influence_circle.geometry.iloc[0])]

        if intersecting_comunas.empty:
            print(f"No se encontraron comunas dentro del radio de influencia para el building en {coords}.")
            continue

        # Obtener los IDs de las comunas intersectadas
        intersecting_ids = intersecting_comunas['objectid'].tolist()

        # Modificar las propiedades de viajes acumulativamente
        def modify_travel_values(row):
            for key in row.index:
                if key.startswith('viajesDiariosDestino_'):
                    destino_id = int(key.split('_')[-1])
                    if destino_id in intersecting_ids:
                        row[key] *= gravity_constant  # Aplicar transformación basada en gravity_constant
            return row

        data_geojson = data_geojson.apply(modify_travel_values, axis=1)

        # Guardar las modificaciones en el archivo temporal
        data_geojson.to_file(temp_geojson, driver="GeoJSON")

    # Leer el archivo temporal final con todas las modificaciones
    data_geojson = gpd.read_file(temp_geojson)

    if debug_shapes:
        # Crear un GeoDataFrame para los círculos de influencia
        circles_gdf = gpd.GeoDataFrame(geometry=[
            gpd.GeoDataFrame.from_features([
                circle(
                    GeoJsonPoint((building['coords'][1], building['coords'][0])),
                    radius=building['local_effect_radius'] / 1000,
                    units="km"
                )
            ]).geometry.iloc[0] for building in buildings
        ], crs="EPSG:4326")

        # Combinar el GeoDataFrame original con los círculos de influencia
        combined_gdf = pd.concat([data_geojson, circles_gdf], ignore_index=True)

        # Guardar el nuevo archivo GeoJSON con círculos de influencia
        output_geojson = input_geojson.replace('.geojson', '_modified_with_circles.geojson')
        combined_gdf.to_file(output_geojson, driver='GeoJSON')
    else:
        # Guardar el nuevo archivo GeoJSON sin círculos de influencia
        output_geojson = input_geojson.replace('.geojson', '_modified.geojson')
        data_geojson.to_file(output_geojson, driver='GeoJSON')

    print(f"Archivo modificado guardado como {output_geojson}")
    return output_geojson


def apply_multiple_gravitational_models_v1(buildings: list, input_geojson: str) -> str:
    # Cargar el GeoJSON inicial
    data_geojson = gpd.read_file(input_geojson)

    # Validar la presencia de 'objectid'
    if 'objectid' not in data_geojson.columns:
        raise ValueError("El archivo GeoJSON no contiene la columna 'objectid'.")

    # Lista para almacenar los círculos de influencia si debug_shapes está habilitado
    influence_circles = [] if debug_shapes else None

    # Iterar sobre cada building y aplicar las transformaciones acumulativamente
    for building in buildings:
        coords = building['coords']
        local_effect_radius = building['local_effect_radius']
        gravity_constant = building['gravity_constant']

        # Crear un círculo de influencia utilizando Turfpy
        center = GeoJsonPoint((coords[1], coords[0]))  # Turfpy usa coordenadas (lon, lat)
        circle_geojson = circle(
            center,
            radius=local_effect_radius / 1000,  # Convertir metros a kilómetros
            units="km"
        )

        influence_circle = gpd.GeoDataFrame.from_features([circle_geojson])
        influence_circle.set_crs("EPSG:4326", inplace=True)

        if debug_shapes:
            influence_circles.append(influence_circle.geometry.iloc[0])

        # Detectar comunas que intersectan con el círculo
        intersecting_comunas = data_geojson[data_geojson.geometry.intersects(influence_circle.geometry.iloc[0])]

        if intersecting_comunas.empty:
            print(f"No se encontraron comunas dentro del radio de influencia para el building en {coords}.")
            continue

        # Obtener los IDs de las comunas intersectadas
        intersecting_ids = intersecting_comunas['objectid'].tolist()

        # Modificar las propiedades de viajes acumulativamente
        def modify_travel_values(row):
            for key in row.index:
                if key.startswith('viajesDiariosDestino_'):
                    destino_id = int(key.split('_')[-1])
                    if destino_id in intersecting_ids:
                        row[key] *= gravity_constant  # Aplicar transformación basada en gravity_constant
            return row

        data_geojson = data_geojson.apply(modify_travel_values, axis=1)

    if debug_shapes:
        # Crear un GeoDataFrame para los círculos de influencia
        circles_gdf = gpd.GeoDataFrame(geometry=influence_circles, crs="EPSG:4326")

        # Combinar el GeoDataFrame original con los círculos de influencia
        combined_gdf = pd.concat([data_geojson, circles_gdf], ignore_index=True)

        # Guardar el nuevo archivo GeoJSON con círculos de influencia
        output_geojson = input_geojson.replace('.geojson', '_modified_with_circles.geojson')
        combined_gdf.to_file(output_geojson, driver='GeoJSON')
    else:
        # Guardar el nuevo archivo GeoJSON sin círculos de influencia
        output_geojson = input_geojson.replace('.geojson', '_modified.geojson')
        data_geojson.to_file(output_geojson, driver='GeoJSON')

    print(f"Archivo modificado guardado como {output_geojson}")
    return output_geojson


# Función para aplicar un modelo gravitacional
def apply_single_gravitational_model(building: dict, input_geojson: str) -> None:
    # Cargar el GeoJSON inicial
    data_geojson = gpd.read_file(input_geojson)

    # Validar la presencia de 'objectid'
    if 'objectid' not in data_geojson.columns:
        raise ValueError("El archivo GeoJSON no contiene la columna 'objectid'.")

    # Extraer parámetros del diccionario
    coords = building['coords']
    local_effect_radius = building['local_effect_radius']
    gravity_constant = building['gravity_constant']
    gravity_decay_exp = building['gravity_decay_exp']
    global_multiplier = building['global_multiplier']

    # Crear un círculo de influencia alrededor de las coordenadas
    point = Point(coords)
    influence_circle = point.buffer(local_effect_radius)

    # Detectar comunas que intersectan con el círculo
    intersecting_comunas = data_geojson[data_geojson.geometry.intersects(influence_circle)]

    if intersecting_comunas.empty:
        print("No se encontraron comunas dentro del radio de influencia.")
        return

    # Obtener los IDs de las comunas intersectadas
    intersecting_ids = intersecting_comunas['objectid'].tolist()

    # Modificar las propiedades de viajes
    def modify_travel_values(row):
        for key in row.index:
            if key.startswith('viajesDiariosDestino_'):
                destino_id = int(key.split('_')[-1])
                if destino_id in intersecting_ids:
                    row[key] *= 1.8  # Aplicar transformación arbitraria (por ahora multiplicar por 1.2)
        return row

    data_geojson = data_geojson.apply(modify_travel_values, axis=1)

    # Guardar el nuevo archivo GeoJSON
    output_geojson = input_geojson.replace('.geojson', '_modified.geojson')
    data_geojson.to_file(output_geojson, driver='GeoJSON')

    print(f"Archivo modificado guardado como {output_geojson}")


# Ejemplo de uso
if __name__ == '__main__':
    buildings = [
        {
            # Mall en pudahuel
            "coords": [-33.44732655513027, -70.76856176807091],
            "local_effect_radius": 3000,
            "gravity_constant": 1.1,
            "gravity_decay_exp": 2,
            "global_multiplier": ("POOR", 200)
        },
        {
            # Mall en la pintana
            "coords": [-33.56194858738686, -70.63790771854241],
            "local_effect_radius": 2500,
            "gravity_constant": 1.1,
            "gravity_decay_exp": 2,
            "global_multiplier": ("MID", 1.1)
        }
    ]

    caracterizacion_comunas = {
        "Santiago": "RICH",
        "San Ramón": "POOR",
        "Providencia": "RICH"
    }

    input_geojson = "GeoJSON_With_Viajes.geojson"
    # apply_single_gravitational_model(buildings[0], input_geojson)

    apply_multiple_gravitational_characteristic_models(buildings, input_geojson, caracterizacion_comunas)

    geojson_graph_list = [
        (r"GeoJSON_With_Viajes.geojson", "BASE"),
        (r"GeoJSON_With_Viajes_modified.geojson", "Modificado Gravitacional")
    ]
    visualization_app.generate_visualizations(geojson_graph_list)
    visualization_app.app.run_server(debug=True)
