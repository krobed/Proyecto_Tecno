import yaml

import visualization_app

YAML_CONFIG_PATH = './config/config.yaml'
YAML_TEMPLATES_PATH = './config/building_templates.yaml'

# Guardo en un diccionario las configuraciones y los templates.
with open(YAML_CONFIG_PATH, 'r') as f:
    config_data = yaml.load(f, Loader=yaml.SafeLoader)

with open(YAML_TEMPLATES_PATH, 'r') as f:
    building_template_data = yaml.load(f, Loader=yaml.SafeLoader)

BASE_SCENARIO = config_data['base_scenario_geojson_path']

# Templates de edificios
TEMPLATE_MALL = building_template_data['mall']
TEMPLATE_DEPTO = building_template_data['complejo_apartamentos']
TEMPLATE_PARQUE = building_template_data['parque_grande']
###


# Lectura entrada ###########
YAML_REQUEST_PATH = input("Ingrese Path de YAML request de calculo: ")
with open(YAML_REQUEST_PATH, 'r') as f:
    requests_dict: dict = yaml.load(f, Loader=yaml.SafeLoader)
#############################

# Funciones de Calculo ########################333
def apply_request(request: dict, input_geojson: str) -> str:
    """

    Retrona como salida el path del geojson que se genero finalmente
    """
    # primero creo una copia del escenario base
    # aplico los calculos sobre esto
    apply_single_gravitational_model()
    apply_global_multiplier()
    # retorno el path de la copia del escenario base, sobre el cual hice las modificaciones
    return output_geojson_path


def apply_single_gravitational_model(building: dict, input_geojson: str) -> None:

    pass


def apply_global_multiplier(group: str, value: float, input_geojson: str) -> None:
    pass


##############################################

# Aplicar solicitudes escenarios
for request, request_data in requests_dict.items():
    print(request, request_data)
    path_geojson_salida = apply_request(request_data)


# Graficar Salida del escenario, comparado el base
visualization_app.run_app([
    (BASE_SCENARIO, "Escenario Base"),
    (path_geojson_salida, "Escenario calculado")
])