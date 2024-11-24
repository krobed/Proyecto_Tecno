from MapMaker import MapMaker


bbox = (-70.69237665060507, -33.46968475646963, -70.6258578743538, -33.43803264216978)
input_geojson = r"C:\Users\pablo\Desktop\EL6101-Proyecto_Tecno\data\Poblacin_Total_Santiago_de_Chile_2012-cud.geojson"

map_maker = MapMaker()
filtered_geojson = map_maker.filter_geojson_by_bbox(input_geojson, bbox)
print(f"GeoJSON filtrado guardado en: {filtered_geojson}")


## generar heatmap
parameter = "pob_tot"
output_html = "mapa_calor.html"

map_maker.generate_heatmap(filtered_geojson, parameter, output_html, title="Población Total")
print(f"Mapa de calor guardado en: {output_html}")


