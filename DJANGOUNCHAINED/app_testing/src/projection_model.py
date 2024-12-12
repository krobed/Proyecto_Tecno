import visualization_app

import yaml
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from turfpy.transformation import circle
from geojson import Point as GeoJsonPoint

# Indica donde esta el yaml de configuracion. hay que rellenarlo
YAML_CONFIG_PATH = 'config.yaml'

# APLICACION DE AJUSTES DE CONFIGURACION ##########################
with open(YAML_CONFIG_PATH, 'r') as f:
    config_data = yaml.load(f, Loader=yaml.SafeLoader)

# DEBUGGING Parámetro para habilitar o deshabilitar la depuración de círculos de influencia
debug_shapes = config_data['debugging']
output_directory = config_data['output_directory']
BASE_SCENARIO = config_data['base_scenario_geojson_path']
YAML_REQUEST_PATH = config_data["request_yaml"]
YAML_TEMPLATES_PATH = config_data["building_templates_yaml"]
YAML_CARACTERIZACION = config_data["caracterizacion_comunas_yaml"]
#############################################################

# CARGA TEMPLATES y caracterizacion ########################################33
with open(YAML_CARACTERIZACION, 'r') as f:
    caracterizacion_comunas = yaml.load(f, Loader=yaml.SafeLoader)

with open(YAML_TEMPLATES_PATH, 'r') as f:
    building_template_data = yaml.load(f, Loader=yaml.SafeLoader)
################################################################


# CARGA SOLICITUDES ###########################################
# Extraigo datos de edificios para solicitud
with open(YAML_REQUEST_PATH, 'r') as f:
    requests_dict: dict = yaml.load(f, Loader=yaml.SafeLoader)

raw_requests_list: list[list[str, list[float, float]]] = requests_dict["requests"]
# print(raw_requests_list)

# Agrego edificios a la lista
buildings_list = []
for building_type, building_coords in raw_requests_list:

    if building_type not in building_template_data:
        print(f"{building_type} no es un tipo de edificio válido!")
        continue

    # Este es el template que corresponde al edificio actual. viene del yaml de templates
    template: dict = building_template_data[building_type]

    building = {
        "type": building_type,
        "coords": building_coords,
        "local_effect_radius": template['local_effect_radius'],
        "gravity_constant": template['gravity_constant'],
        "global_multiplier": template["global_multiplier"]
    }

    # print(f"Agregado a calculo edificio con parametros {building}")
    buildings_list.append(building)

print(f"\nLista de edificios a simular: ------------------")
for building in buildings_list:
    print(building)
print("---------------------------------------------------")
######################################################


# Funciones de Calculo ###############################
def apply_multiple_gravitational_characteristic_models(buildings: list[dict], input_geojson: str,
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


##############################################

# Ejecutable
if __name__ == "__main__":

    output_path = apply_multiple_gravitational_characteristic_models(buildings_list, BASE_SCENARIO, caracterizacion_comunas)

    geojson_graph_list = [
        (BASE_SCENARIO, "Escenario base - Numero viajes de destino a comuna diario - EOD 2012 /EMS 2024"),
        (output_path, "Escenario Calculado - Numero Viajes de destino a comuna diario")
    ]

    # llamo a la api de visualizacion
    visualization_app.generate_visualizations(geojson_graph_list, debug_shapes=debug_shapes,buildings=buildings_list)
    visualization_app.app.run_server(debug=True,host='127.0.0.1', port='8050')
