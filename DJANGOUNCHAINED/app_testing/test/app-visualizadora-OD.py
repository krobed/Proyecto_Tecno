import dash
from dash import dcc, html, Input, Output
import geopandas as gpd
import pandas as pd
import plotly.express as px

# Cargar el GeoJSON y preparar los datos
geojson_path = "GeoJSON_With_Viajes.geojson"
data_geojson = gpd.read_file(geojson_path)

# Asegurar que el GeoJSON tiene una clave de identificación única
if 'objectid' not in data_geojson.columns:
    raise ValueError("El archivo GeoJSON no contiene la columna 'objectid'.")

# Preparar las opciones del dropdown
comunas = data_geojson['Comuna'].unique()
comuna_options = [{'label': comuna, 'value': comuna} for comuna in comunas]

# Inicializar la aplicación Dash
app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Dropdown(
        id='comuna-dropdown',
        options=comuna_options,
        value='SANTIAGO',  # Valor inicial
        placeholder="Seleccione una comuna",
        style={'width': '50%', 'margin': '0 auto'}
    ),
    dcc.Graph(
        id='choropleth-map',
        style={'height': '100vh', 'width': '100vw'},
        config={
            'scrollZoom': True  # Permitir zoom con la rueda del ratón
        }
    )
])

@app.callback(
    Output('choropleth-map', 'figure'),
    [Input('comuna-dropdown', 'value')]
)
def update_map(selected_comuna):
    if not selected_comuna:
        return {}

    # Filtrar los datos para la comuna seleccionada
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

    # Crear la figura coroplética
    fig = px.choropleth_mapbox(
        merged_data,
        geojson=merged_data.__geo_interface__,
        locations='objectid',
        color='value',
        hover_name='Comuna',
        mapbox_style="carto-positron",
        center={"lat": -33.45, "lon": -70.65},
        zoom=10,  # Ajustar el zoom para ver todas las comunas correctamente
        color_continuous_scale="YlOrRd",
        featureidkey="properties.objectid"
    )

    # Ajustar la transparencia
    fig.update_traces(marker_opacity=0.5)  # Mayor transparencia

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
