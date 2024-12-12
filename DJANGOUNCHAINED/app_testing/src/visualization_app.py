import dash
from dash import dcc, html, Input, Output
import geopandas as gpd
import pandas as pd
import plotly.express as px
from flask import Flask

# Inicializar el servidor y la aplicación Dash
server = Flask(__name__)
app = dash.Dash(__name__, server=server, url_base_pathname='/')

# Asegurar que el GeoJSON tiene una clave de identificación única
def validate_geojson(data_geojson):
    if 'objectid' not in data_geojson.columns:
        raise ValueError("El archivo GeoJSON no contiene la columna 'objectid'.")

# Crear las opciones para el dropdown
def get_comuna_options(data_geojson):
    comunas = data_geojson['Comuna'].dropna().unique()  # Eliminar valores NaN o None
    return [{'label': comuna, 'value': comuna} for comuna in comunas]

# Crear una función de actualización de la figura coroplética
def create_figure(data_geojson, selected_comuna, debug_shapes, buildings):
    if not selected_comuna:
        return {}

    comuna_data = data_geojson[data_geojson['Comuna'].str.upper() == selected_comuna.upper()]

    if comuna_data.empty:
        return {}

    choropleth_data = []
    for _, row in comuna_data.iterrows():
        for key, value in row.items():
            if key.startswith('viajesDiariosDestino_') and value > 0:
                destino_id = int(key.split('_')[-1])
                choropleth_data.append({'objectid': destino_id, 'value': value})

    choropleth_df = pd.DataFrame(choropleth_data)
    merged_data = data_geojson.merge(choropleth_df, on='objectid', how='left').fillna({'value': 0})

    fig = px.choropleth_mapbox(
        merged_data,
        geojson=merged_data.__geo_interface__,
        locations='objectid',
        color='value',
        hover_name='Comuna',
        mapbox_style="carto-positron",
        center={"lat": -33.45, "lon": -70.65},
        zoom=10,
        color_continuous_scale="YlOrRd",
        featureidkey="properties.objectid"
    )

    fig.update_traces(marker_opacity=0.6)

    if buildings:
        # Añadir puntos de edificios al mapa
        for building in buildings:
            coords = building['coords']
            building_type = building['type']
            fig.add_scattermapbox(
                lon=[coords[1]],
                lat=[coords[0]],
                mode="markers",
                marker=dict(size=10, color=px.colors.qualitative.Set1[hash(building_type) % len(px.colors.qualitative.Set1)]),
                name=building_type
            )

    return fig

# Crear una función para calcular la diferencia entre dos GeoJSONs
def create_difference_figure(base_geojson, scenario_geojson, selected_comuna):
    if not selected_comuna:
        return {}

    comuna_data_base = base_geojson[base_geojson['Comuna'].str.upper() == selected_comuna.upper()]
    comuna_data_scenario = scenario_geojson[scenario_geojson['Comuna'].str.upper() == selected_comuna.upper()]

    if comuna_data_base.empty or comuna_data_scenario.empty:
        return {}

    diff_data = []
    for _, base_row in comuna_data_base.iterrows():
        for key, base_value in base_row.items():
            if key.startswith('viajesDiariosDestino_'):
                destino_id = int(key.split('_')[-1])
                scenario_value = comuna_data_scenario.iloc[0].get(key, 0)
                diff_data.append({'objectid': destino_id, 'value': scenario_value - base_value})

    diff_df = pd.DataFrame(diff_data)
    merged_diff = base_geojson.merge(diff_df, on='objectid', how='left').fillna({'value': 0})

    fig = px.choropleth_mapbox(
        merged_diff,
        geojson=merged_diff.__geo_interface__,
        locations='objectid',
        color='value',
        hover_name='Comuna',
        mapbox_style="carto-positron",
        center={"lat": -33.45, "lon": -70.65},
        zoom=10,
        color_continuous_scale="RdBu",
        featureidkey="properties.objectid"
    )

    fig.update_traces(marker_opacity=0.6)
    return fig

# Función principal para generar múltiples visualizaciones
def generate_visualizations(geojson_graph_list, buildings, debug_shapes):
    layouts = []

    data_geojsons = []
    for geojson_path, graph_name in geojson_graph_list:
        data_geojson = gpd.read_file(geojson_path)
        validate_geojson(data_geojson)
        comuna_options = get_comuna_options(data_geojson)
        data_geojsons.append(data_geojson)

        layout = html.Div([
            html.H3(f"Visualización: {graph_name}"),
            dcc.Dropdown(
                id=f'comuna-dropdown-{graph_name}',
                options=comuna_options,
                value='SANTIAGO',
                placeholder="Seleccione una comuna",
                style={'width': '50%', 'margin': '0 auto'}
            ),
            dcc.Graph(
                id=f'choropleth-map-{graph_name}',
                style={'height': '90vh', 'width': '100%'},
                config={'scrollZoom': True}
            )
        ])

        layouts.append((layout, graph_name, data_geojson))

    if len(data_geojsons) == 2:
        diff_layout = html.Div([
            html.H3("Diferencia entre Escenarios"),
            dcc.Dropdown(
                id='comuna-dropdown-difference',
                options=get_comuna_options(data_geojsons[0]),
                value='SANTIAGO',
                placeholder="Seleccione una comuna",
                style={'width': '50%', 'margin': '0 auto'}
            ),
            dcc.Graph(
                id='choropleth-map-difference',
                style={'height': '90vh', 'width': '100%'},
                config={'scrollZoom': True}
            )
        ])

        layouts.append((diff_layout, "Diferencia", data_geojsons))

    app.layout = html.Div([
        dcc.Tabs([
            dcc.Tab(label=graph_name, children=layout)
            for layout, graph_name, _ in layouts
        ])
    ])

    for layout, graph_name, data_geojson in layouts[:-1]:
        @app.callback(
            Output(f'choropleth-map-{graph_name}', 'figure'),
            [Input(f'comuna-dropdown-{graph_name}', 'value')]
        )
        def update_map(selected_comuna, data_geojson=data_geojson, buildings=buildings):
            return create_figure(data_geojson, selected_comuna, debug_shapes, buildings)

    if len(data_geojsons) == 2:
        base_geojson, scenario_geojson = data_geojsons

        @app.callback(
            Output('choropleth-map-difference', 'figure'),
            [Input('comuna-dropdown-difference', 'value')]
        )
        def update_difference_map(selected_comuna):
            return create_difference_figure(base_geojson, scenario_geojson, selected_comuna)

# Función para ejecutar el servidor desde otro módulo
def run_app(geojson_graph_list: list[(str, str)], buildings: list[dict], debug_shapes=True):
    """
    Ejecuta la aplicacion de visualización de archivos GeoJSON con el formato
    estandar de pares OD definidos por comunas

    Args:
        geojson_graph_list: Una lista de tuplas del estilo (path_archivo_geojson, nombre_visualizacion).
        buildings: Lista de diccionarios con información de edificios a agregar como puntos.

    La idea seria que la primera tupla siemrpe sea la visualización base de OD de comuans de santiago.
    y todas las tuplas que vienen sean "escenarios" distintos, con nombres distintos.
    """
    generate_visualizations(geojson_graph_list, buildings, debug_shapes)
    app.run_server(debug=True)

# Ejemplo de uso
if __name__ == '__main__':
    pass
    # ESTO ES UN EJEMPLO DE USO, POR FAVOR LLAMAR A ESTO DESDE OTRO SCRIPT SIEMRPE.
    # geojson_graph_list = [
    #     ("GeoJSON_With_Viajes.geojson", "Graph 1"),
    #     ("GeoJSON_With_Viajes_2.geojson", "Graph 2")
    # ]
    # run_app(geojson_graph_list)
