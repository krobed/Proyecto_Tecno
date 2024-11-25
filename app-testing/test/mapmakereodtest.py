import sys
sys.path.insert(1, '/home/winkrobed/Proyecto_Tecno/app-testing/src')

#%%
from MapMaker import MapMaker



def map_maker_eod(inf_der,sup_izq, comuna):
    input_geojson = r"~/Proyecto_Tecno/data/Cantidad_de_viajes_de_destino_EOD_06.geojson"

    map_maker = MapMaker()
    filtered_geojson = map_maker.filter_geojson_by_bbox(input_geojson,sup_izq,inf_der)
    print(f"GeoJSON filtrado guardado en: {filtered_geojson}")

    ## generar heatmap
    parameter = "viaj_dest" # aca igual está segregado por tipo de viaje: compras_06, salud_06, ...
    output_html = f"/home/winkrobed/Proyecto_Tecno/DJANGOUNCHAINED/polls/templates/mapa_calor-EOD_{comuna}.html"

    map_maker.generate_heatmap(filtered_geojson, parameter, output_html, title="Viajes con destino sector - EOD")
    print(f"Mapa de calor guardado en: {output_html}")
