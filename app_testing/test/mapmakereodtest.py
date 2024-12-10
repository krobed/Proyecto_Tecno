import sys
import os
path = os.path.abspath(r"")
sys.path.insert(1,path[:-17])
from app_testing.src.MapMaker import MapMaker
pato = path[:-17]


def map_maker_eod(inf_der,sup_izq, comuna):
    input_geojson = f"{pato}/data/Cantidad_de_viajes_de_destino_EOD_06.geojson"

    map_maker = MapMaker()
    filtered_geojson = map_maker.filter_geojson_by_bbox(input_geojson,sup_izq,inf_der)
    print(f"GeoJSON filtrado guardado en: {filtered_geojson}")

    ## generar heatmap
    parameter = "viaj_dest" # aca igual está segregado por tipo de viaje: compras_06, salud_06, ...
    output_html = f"{pato}/DJANGOUNCHAINED/polls/templates/mapa_calor-EOD_{comuna}.html"

    map_maker.generate_heatmap(filtered_geojson, parameter, output_html, title="Viajes con destino sector - EOD")
    print(f"Mapa de calor guardado en: {output_html}")
