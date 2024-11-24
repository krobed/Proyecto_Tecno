from MapMaker import MapMaker


esquina_superior_izquierda = -33.41449365894426, -70.75006766509088
esquina_inferior_derecha = -33.515023008314486, -70.55780694267634
input_geojson = r"C:\Users\pablo\Desktop\EL6101-Proyecto_Tecno\data\Cantidad_de_viajes_de_destino_EOD_06.geojson"

map_maker = MapMaker()
filtered_geojson = map_maker.filter_geojson_by_bbox(input_geojson, esquina_superior_izquierda, esquina_inferior_derecha)
print(f"GeoJSON filtrado guardado en: {filtered_geojson}")



## generar heatmap
parameter = "viaj_dest" # aca igual está segregado por tipo de viaje: compras_06, salud_06, ...
output_html = "mapa_calor-EOD.html"

map_maker.generate_heatmap(filtered_geojson, parameter, output_html, title="Viajes con destino sector - EOD")
print(f"Mapa de calor guardado en: {output_html}")
