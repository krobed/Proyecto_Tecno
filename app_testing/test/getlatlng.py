import gradio as gr
from gradio_folium import Folium
from folium import Map, Element, LatLngPopup
import pandas as pd
import pathlib

def click(coord):
    print(coord)

def inject_javascript(folium_map):
    script = """<script>
    document.addEventListener('DOMContentLoaded', function() {
        map_name_1.on('click', function(e) {
            window.state_data = e.latlng
        });
    });
    </script>
    """
    folium_map.get_root().html.add_child(Element(script))

with gr.Blocks() as demo:
    map = Map(location=[25.7617, 80.1918])
    map._name, map._id = "map_name", "1"

    LatLngPopup().add_to(map)

    inject_javascript(map)
    fol = Folium(value=map, height=400, elem_id="map-component")
    txt = gr.Textbox(value="No coordinates selected", label="Latitude, Longitude", elem_id="coord-component", visible=False)
    js =  """
    (textBox) => {
        const iframeMap = document.getElementById('map-component').getElementsByTagName('iframe')[0];
        const latlng = iframeMap.contentWindow.state_data;
        if (!latlng) { return; }
        //document.getElementById('coord-component').getElementsByTagName('textarea')[0].value = `${latlng.lat},${latlng.lng}`;
        return `${latlng.lat},${latlng.lng}`;
    }
    """
    button = gr.Button("Get results")
    button.click(click, inputs=[txt], js=js)

demo.launch()