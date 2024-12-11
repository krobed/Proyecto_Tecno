import sys
import os
path = os.path.abspath(r"")
from app_testing.src.MapMaker import MapMaker
pato = path

def map_maker(inf_der,sup_izq, comuna):
    input_geojson = f"{pato}/data/xn--Poblacin_Total_Santiago_de_Chile_2012-cud.geojson"

    map_maker = MapMaker()
    filtered_geojson = map_maker.filter_geojson_by_bbox(input_geojson, sup_izq,inf_der)
    print(f"GeoJSON filtrado guardado en: {filtered_geojson}")



    ## generar heatmap
    parameter = "pob_tot"
    output_html = f"{pato}/nukemapu_app/templates/mapa_calor_{comuna}.html"

    map_maker.generate_heatmap(filtered_geojson, parameter, output_html, title="Población Total")
    print(f"Mapa de calor guardado en: {output_html}")


