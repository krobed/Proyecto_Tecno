import visualization_app
"""
Asi se debe usar las llamadas a la api de visualización.
"""
geojson_graph_list = [
    ("GeoJSON_With_Viajes.geojson", "Escenario Base"),
    ("GeoJSON_With_Viajes.geojson", "Escenario Prueba - Mall")
]

visualization_app.run_app(geojson_graph_list)