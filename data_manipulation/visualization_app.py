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
    comunas = data_geojson['Comuna'].unique()
    return [{'label': comuna, 'value': comuna} for comuna in comunas]

# Crear una función de actualización de la figura coroplética
def create_figure(data_geojson, selected_comuna):
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

    fig.update_traces(marker_opacity=0.3)
    return fig

# Función principal para generar múltiples visualizaciones
def generate_visualizations(geojson_graph_list):
    layouts = []

    for geojson_path, graph_name in geojson_graph_list:
        data_geojson = gpd.read_file(geojson_path)
        validate_geojson(data_geojson)
        comuna_options = get_comuna_options(data_geojson)

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

    app.layout = html.Div([
        dcc.Tabs([
            dcc.Tab(label=graph_name, children=layout)
            for layout, graph_name, _ in layouts
        ])
    ])

    for layout, graph_name, data_geojson in layouts:
        @app.callback(
            Output(f'choropleth-map-{graph_name}', 'figure'),
            [Input(f'comuna-dropdown-{graph_name}', 'value')]
        )
        def update_map(selected_comuna, data_geojson=data_geojson):
            return create_figure(data_geojson, selected_comuna)

if __name__ == '__main__':
    geojson_graph_list = [
        (r"C:\Users\pablo\Escritorio\EL6101-Proyecto_Tecno\data_manipulation\GeoJSON_With_Viajes.geojson", "Graph 1"),
        (r"C:\Users\pablo\Escritorio\EL6101-Proyecto_Tecno\data_manipulation\GeoJSON_With_Viajes.geojson", "Graph 2")
    ]
    generate_visualizations(geojson_graph_list)
    app.run_server(debug=True)
