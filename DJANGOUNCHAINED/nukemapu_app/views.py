from django.http import HttpResponse
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
import time
from datetime import datetime as dt
import sys
import os
import yaml
import numpy as np
path = os.path.abspath(r"")
print(path)
from app_testing.src.mapmakereodtest import map_maker_eod
from app_testing.src.mapmakertest import map_maker

pato = path

comunas = yaml.safe_load(open(f'{pato}/nukemapu_app/static/poligonos_comuna.yml', 'r'))
yaml_path = f'{pato}/app_testing/src/requests/'
if not os.path.exists(yaml_path):
    os.mkdir(yaml_path)
from .forms import CoordenadasForm
import json


def formulario_view(request):
    if request.method == "POST":
        form = CoordenadasForm(request.POST)
        if form.is_valid():
            # Obtener todos los marcadores como lista de coordenadas
            todos_los_marcadores = form.cleaned_data['todos_los_marcadores']
            estructura = form.cleaned_data['estructura']
            estructura = estructura.lower()
            if estructura == 'parque':
                estructura ='parque_grande'
            else:
                estructura = 'complejo_apartamentos'
            
            marcadores = json.loads(todos_los_marcadores) if todos_los_marcadores else []
            l = []
            for marcador in marcadores:
                l.append({'type':estructura,'coordinates':marcador})
            # Procesar la lista de marcadores
            
            if not os.path.exists(f'{yaml_path}/calculation_request.yaml'):
                yamil =open(f'{yaml_path}/calculation_request.json', 'x',)
            else:
                yamil =  open(f'{yaml_path}/calculation_request.json', 'w',)
            
            json.dump({'request':l,'timestamp':str(dt.now())},yamil)
            
            yamil.close()
            return HttpResponse(f"Se recibieron {len(marcadores)} marcadores: {marcadores}.")
    else:
        form = CoordenadasForm()
    return render(request, 'formulario.html', {'form': form})




def home(request):
    if request.method == "POST":
        if 'mapa' in request.POST:
            form = CoordenadasForm()
            return render(request, "formulario.html", {'form': form})
        else:
            global comunas
            return render(request, "home.html", context=comunas)
    else:
        return render(request, "index.html")


def index(request):
    global comunas
    return render(request, "home.html", context=comunas)


def goto(request):
    global comunas
    comuna = request.POST.get("comuna")

    if int(comuna) - 1 < len(comunas['Comunas']):
        comuna = comunas['Comunas'][int(comuna) - 1]
        nombre = comuna['nombre']
        inf_der = float(comuna['coords'][0][1:]), float(comuna['coords'][1][:-1])
        sup_izq = float(comuna['coords'][2][1:]), float(comuna['coords'][3][:-1])
    else:
        raise IndexError
    if "densidad" in request.POST:
        if os.path.exists(f'{pato}/nukemapu_app/templates/mapa_calor_{nombre}.html'):
            return render(request, f'mapa_calor_{nombre}.html')
        else:
            map_maker(inf_der, sup_izq, nombre)
            if os.path.exists(f'{pato}/nukemapu_app/templates/mapa_calor_{nombre}.html'):
                return render(request, f'mapa_calor_{nombre}.html')
            else:
                time.sleep(1)
                return render(request, f'mapa_calor_{nombre}.html')
    if "eod" in request.POST:
        if os.path.exists(f'{pato}/nukemapu_app/templates/mapa_calor-EOD_{nombre}.html'):
            return render(request, f'mapa_calor-EOD_{nombre}.html')
        else:
            map_maker_eod(inf_der, sup_izq, nombre)
            if os.path.exists(f'{pato}/nukemapu_app/templates/mapa_calor-EOD_{nombre}.html'):
                return render(request, f'mapa_calor-EOD_{nombre}.html')
            else:
                time.sleep(1)
                return render(request, f'mapa_calor-EOD_{nombre}.html')
