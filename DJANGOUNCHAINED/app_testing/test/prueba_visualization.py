import folium
import geopandas as gpd
from folium import GeoJson
import json

import folium
import geopandas as gpd
import json
import os

# Función principal
def generate_interactive_choropleth_map_2(geojson_path, output_html):
    # Cargar el GeoJSON
    data_geojson = gpd.read_file(geojson_path)

    # Crear datos iniciales para SANTIAGO
    def get_initial_data():
        comuna_santiago = data_geojson[data_geojson['Comuna'].str.upper() == 'SANTIAGO']

        if comuna_santiago.empty:
            raise ValueError("No se encontró la comuna de SANTIAGO en el archivo GeoJSON.")

        choropleth_data = []
        for _, row in comuna_santiago.iterrows():
            for key, value in row.items():
                if key.startswith('viajesDiariosDestino_') and value > 0:
                    destino_id = int(key.split('_')[-1])
                    choropleth_data.append({'objectid': destino_id, 'value': value})

        return pd.DataFrame(choropleth_data)

    import pandas as pd
    choropleth_df = get_initial_data()

    # Asociar los valores iniciales a los shapes
    data_geojson = data_geojson.merge(choropleth_df, on='objectid', how='left').fillna({'value': 0})

    # Crear el mapa centrado en Santiago
    mapa = folium.Map(location=[-33.45, -70.65], zoom_start=12)  # Coordenadas aproximadas de Santiago

    # Agregar el mapa coroplético
    folium.Choropleth(
        geo_data=data_geojson,
        data=choropleth_df,
        columns=['objectid', 'value'],
        key_on='feature.properties.objectid',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Viajes desde SANTIAGO'
    ).add_to(mapa)

    # Crear un dropdown y un botón para generar un nuevo mapa
    script_content = """
    <script>
    var geojson = {geojson_data};

    function generateNewMap(comunaName) {
        let selectedFeature = geojson.features.find(feature => feature.properties.Comuna.toUpperCase() === comunaName.toUpperCase());

        if (!selectedFeature) {
            console.error("Comuna no encontrada: " + comunaName);
            return;
        }

        let viajes = selectedFeature.properties;
        let updates = {};

        Object.keys(viajes).forEach(key => {
            if (key.startsWith('viajesDiariosDestino_')) {
                let destinoID = parseInt(key.split('_')[1]);
                updates[destinoID] = viajes[key];
            }
        });

        geojson.features.forEach(function(feat) {
            let id = feat.properties.objectid;
            feat.properties.value = updates[id] || 0;
        });

        let newHtmlContent = JSON.stringify(geojson);
        let newFileName = "map_" + comunaName + ".html";

        fetch("/save_map", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                geojson: geojson,
                filename: newFileName
            })
        }).then(response => {
            if (response.ok) {
                window.open(newFileName, '_blank');
            } else {
                console.error("Error al guardar el nuevo mapa");
            }
        });
    }

    function createDropdownAndButton() {
        let container = document.createElement('div');
        container.style.position = 'absolute';
        container.style.top = '10px';
        container.style.left = '50%';
        container.style.transform = 'translateX(-50%)';
        container.style.zIndex = '1000';
        container.style.backgroundColor = 'white';
        container.style.padding = '10px';
        container.style.borderRadius = '5px';
        container.style.boxShadow = '0 2px 5px rgba(0,0,0,0.3)';

        let dropdown = document.createElement('select');
        dropdown.setAttribute('id', 'comuna-selector');
        dropdown.style.marginRight = '10px';

        geojson.features.forEach(function(feature) {
            let option = document.createElement('option');
            option.value = feature.properties.Comuna;
            option.textContent = feature.properties.Comuna;
            dropdown.appendChild(option);
        });

        let button = document.createElement('button');
        button.textContent = 'Generar Mapa';
        button.onclick = function() {
            let comunaName = dropdown.value;
            generateNewMap(comunaName);
        };

        container.appendChild(dropdown);
        container.appendChild(button);
        document.body.appendChild(container);
    }

    createDropdownAndButton();
    </script>
    """.replace("{geojson_data}", json.dumps(data_geojson.__geo_interface__))

    mapa.get_root().html.add_child(folium.Element(script_content))

    # Guardar el mapa
    mapa.save(output_html)
    print(f"Archivo HTML interactivo generado: {output_html}")

# Función principal
def generate_interactive_choropleth_map(geojson_path, output_html):
    # Cargar el GeoJSON
    data_geojson = gpd.read_file(geojson_path)

    # Crear datos iniciales para SANTIAGO
    def get_initial_data():
        comuna_santiago = data_geojson[data_geojson['Comuna'].str.upper() == 'SANTIAGO']

        if comuna_santiago.empty:
            raise ValueError("No se encontró la comuna de SANTIAGO en el archivo GeoJSON.")

        choropleth_data = []
        for _, row in comuna_santiago.iterrows():
            for key, value in row.items():
                if key.startswith('viajesDiariosDestino_') and value > 0:
                    destino_id = int(key.split('_')[-1])
                    choropleth_data.append({'objectid': destino_id, 'value': value})

        return pd.DataFrame(choropleth_data)

    import pandas as pd
    choropleth_df = get_initial_data()

    # Asociar los valores iniciales a los shapes
    data_geojson = data_geojson.merge(choropleth_df, on='objectid', how='left').fillna({'value': 0})

    # Crear el mapa centrado en Santiago
    mapa = folium.Map(location=[-33.45, -70.65], zoom_start=12)  # Coordenadas aproximadas de Santiago

    # Agregar el mapa coroplético
    folium.Choropleth(
        geo_data=data_geojson,
        data=choropleth_df,
        columns=['objectid', 'value'],
        key_on='feature.properties.objectid',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Viajes desde SANTIAGO'
    ).add_to(mapa)

    # Crear un dropdown y un botón para seleccionar la comuna
    script_content = """
    <script>
    var geojson = {geojson_data};

    function updateChoropleth(comunaName) {
        let selectedFeature = geojson.features.find(feature => feature.properties.Comuna.toUpperCase() === comunaName.toUpperCase());

        if (!selectedFeature) {
            console.error("Comuna no encontrada: " + comunaName);
            return;
        }

        let viajes = selectedFeature.properties;
        let updates = {};

        Object.keys(viajes).forEach(key => {
            if (key.startsWith('viajesDiariosDestino_')) {
                let destinoID = parseInt(key.split('_')[1]);
                updates[destinoID] = viajes[key];
            }
        });

        geojson.features.forEach(function(feat) {
            let id = feat.properties.objectid;
            feat.properties.value = updates[id] || 0;
        });

        map.eachLayer(function(layer) {
            if (layer.options && layer.options.name === 'choropleth') {
                map.removeLayer(layer);
            }
        });

        L.choropleth(geojson, {
            valueProperty: 'value',
            scale: ['#ffffb2', '#b10026'],
            steps: 10,
            mode: 'q',
            style: {
                color: '#fff',
                weight: 2,
                fillOpacity: 0.7
            },
        }).addTo(map);
    }

    function createDropdownAndButton() {
        let container = document.createElement('div');
        container.style.position = 'absolute';
        container.style.top = '10px';
        container.style.left = '50%';
        container.style.transform = 'translateX(-50%)';
        container.style.zIndex = '1000';
        container.style.backgroundColor = 'white';
        container.style.padding = '10px';
        container.style.borderRadius = '5px';
        container.style.boxShadow = '0 2px 5px rgba(0,0,0,0.3)';

        let dropdown = document.createElement('select');
        dropdown.setAttribute('id', 'comuna-selector');
        dropdown.style.marginRight = '10px';

        geojson.features.forEach(function(feature) {
            let option = document.createElement('option');
            option.value = feature.properties.Comuna;
            option.textContent = feature.properties.Comuna;
            dropdown.appendChild(option);
        });

        let button = document.createElement('button');
        button.textContent = 'Seleccionar';
        button.onclick = function() {
            let comunaName = dropdown.value;
            updateChoropleth(comunaName);
        };

        container.appendChild(dropdown);
        container.appendChild(button);
        document.body.appendChild(container);
    }

    createDropdownAndButton();
    </script>
    """.replace("{geojson_data}", json.dumps(data_geojson.__geo_interface__))

    mapa.get_root().html.add_child(folium.Element(script_content))

    # Guardar el mapa
    mapa.save(output_html)
    print(f"Archivo HTML interactivo generado: {output_html}")

# Función principal
def generate_interactive_overlay(geojson_path, output_html):
    # Cargar el GeoJSON
    data_geojson = gpd.read_file(geojson_path)

    # Reproyectar las geometrías a un CRS proyectado para calcular los centroides correctamente
    data_geojson = data_geojson.to_crs(epsg=3857)

    # Calcular el centroide de cada shape y convertirlo a coordenadas JSON serializables
    data_geojson["centroid_coords"] = data_geojson.geometry.centroid.apply(lambda point: [point.y, point.x])

    # Volver a CRS geográfico para la visualización en el mapa
    data_geojson = data_geojson.to_crs(epsg=4326)

    # Crear el mapa centrado
    center = [
        data_geojson["centroid_coords"].apply(lambda x: x[0]).mean(),
        data_geojson["centroid_coords"].apply(lambda x: x[1]).mean()
    ]
    mapa = folium.Map(location=center, zoom_start=11)

    # Extraer centroides como un diccionario para JavaScript
    centroids = {
        int(row["objectid"]): row["centroid_coords"]
        for _, row in data_geojson.iterrows()
    }

    # Crear la capa GeoJSON
    geojson_layer = GeoJson(
        data_geojson,
        name="Comunas",
        tooltip=folium.GeoJsonTooltip(fields=["objectid"], aliases=["Comuna ID"]),
        style_function=lambda x: {
            "fillColor": "#ADD8E6",
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.5,
        },
        highlight_function=lambda x: {"weight": 3, "color": "green"},
    )

    geojson_layer.add_to(mapa)

    # Agregar lógica de Heatmap dinámico
    script_content = """
    <script>
    var centroids = {centroids_data};

    function updateHeatmap(feature) {
        let comunaID = feature.properties.objectid;
        let viajes = feature.properties;

        map.eachLayer(function (layer) {
            if (layer.options && layer.options.className === 'dynamic-heatmap') {
                map.removeLayer(layer);
            }
        });

        let heatmapData = [];
        for (let key in viajes) {
            if (key.startsWith('viajesDiariosDestino_')) {
                let destinoID = key.split('_')[1];
                let sumaViajes = viajes[key];
                if (sumaViajes > 0) {
                    let destino = centroids[destinoID];
                    if (destino) {
                        heatmapData.push([destino[0], destino[1], sumaViajes]);
                    }
                }
            }
        }

        L.heatLayer(heatmapData, {
            radius: 25,
            blur: 15,
            maxZoom: 17,
            className: 'dynamic-heatmap'
        }).addTo(map);
    }

    var geojson = L.geoJson({geojson_data}, {
        onEachFeature: function (feature, layer) {
            layer.on('click', function () {
                updateHeatmap(feature);
            });
        }
    });

    geojson.addTo(map);
    </script>
    """.replace("{centroids_data}", json.dumps(centroids)).replace("{geojson_data}", json.dumps(data_geojson.__geo_interface__))

    mapa.get_root().html.add_child(folium.Element(script_content))

    # Guardar el mapa
    mapa.save(output_html)
    print(f"Archivo HTML guardado como: {output_html}")


import folium
import geopandas as gpd
from folium.plugins import HeatMap

# Función principal

import folium
import geopandas as gpd
from folium.plugins import HeatMap

# Función principal

def generate_static_heatmap(geojson_path, output_html):
    # Cargar el GeoJSON
    data_geojson = gpd.read_file(geojson_path)

    # Filtrar la comuna de SANTIAGO
    comuna_santiago = data_geojson[data_geojson['Comuna'].str.upper() == 'SANTIAGO']

    if comuna_santiago.empty:
        raise ValueError("No se encontró la comuna de SANTIAGO en el archivo GeoJSON.")

    # Obtener los datos de viajes desde SANTIAGO hacia otras comunas
    viajes_data = []
    for _, row in comuna_santiago.iterrows():
        for key, value in row.items():
            if key.startswith('viajesDiariosDestino_') and value > 0:
                destino_id = int(key.split('_')[-1])
                destino_geom = data_geojson[data_geojson['objectid'] == destino_id].geometry

                if not destino_geom.empty:
                    centroid = destino_geom.iloc[0].centroid
                    viajes_data.append([centroid.y, centroid.x, value])

    # Crear el mapa centrado en Santiago
    mapa = folium.Map(location=[-33.45, -70.65], zoom_start=12)  # Coordenadas aproximadas de Santiago

    # Agregar el Heatmap
    HeatMap(viajes_data, radius=25, blur=15, max_zoom=17).add_to(mapa)

    # Guardar el mapa
    mapa.save(output_html)
    print(f"Mapa estático de Heatmap generado: {output_html}")



import folium
import geopandas as gpd

# Función principal
def generate_choropleth_map(geojson_path, output_html):
    # Cargar el GeoJSON
    data_geojson = gpd.read_file(geojson_path)

    # Filtrar la comuna de SANTIAGO
    comuna_santiago = data_geojson[data_geojson['Comuna'].str.upper() == 'SANTIAGO']

    if comuna_santiago.empty:
        raise ValueError("No se encontró la comuna de SANTIAGO en el archivo GeoJSON.")

    # Crear un DataFrame con los valores de viajesDiariosDestino
    choropleth_data = []
    for _, row in comuna_santiago.iterrows():
        for key, value in row.items():
            if key.startswith('viajesDiariosDestino_') and value > 0:
                destino_id = int(key.split('_')[-1])
                choropleth_data.append({'objectid': destino_id, 'value': value})

    # Convertir a DataFrame
    import pandas as pd
    choropleth_df = pd.DataFrame(choropleth_data)

    # Asociar los valores a los shapes
    data_geojson = data_geojson.merge(choropleth_df, on='objectid', how='left').fillna({'value': 0})

    # Crear el mapa centrado en Santiago
    mapa = folium.Map(location=[-33.45, -70.65], zoom_start=12)  # Coordenadas aproximadas de Santiago

    # Agregar el mapa coroplético
    folium.Choropleth(
        geo_data=data_geojson,
        data=choropleth_df,
        columns=['objectid', 'value'],
        key_on='feature.properties.objectid',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Viajes desde SANTIAGO'
    ).add_to(mapa)

    # Guardar el mapa
    mapa.save(output_html)
    print(f"Mapa coroplético generado: {output_html}")