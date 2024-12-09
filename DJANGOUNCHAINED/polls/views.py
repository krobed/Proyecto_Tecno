from django.http import HttpResponse
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
import time
import sys
import os
import yaml
import geocoder

sys.path.insert(1, '/home/winkrobed/Proyecto_Tecno/app-testing/test')
from mapmakereodtest import map_maker_eod
from mapmakertest import map_maker
sys.path.insert(2, '/home/winkrobed/Proyecto_Tecno/data')
comunas = yaml.safe_load(open('/home/winkrobed/Proyecto_Tecno/data/poligonos_comuna.yml','r'))

import folium as fl
from streamlit_folium import st_folium
import streamlit as st
from django.http import JsonResponse
from .models import Coordenada
from .forms import CoordenadasForm
import json

def formulario_view(request):
    if request.method == "POST":
        form = CoordenadasForm(request.POST)
        if form.is_valid():
            latitud = form.cleaned_data['latitud']
            longitud = form.cleaned_data['longitud']
            # Aquí puedes manejar las coordenadas, como guardarlas en la base de datos
            return HttpResponse(f"Coordenadas recibidas: Latitud {latitud}, Longitud {longitud}")
    else:
        form = CoordenadasForm()
    return render(request, 'formulario.html', {'form': form})

def guardar_coordenadas(request):
    if request.method == "POST":
        data = json.loads(request.body)
        lat = data.get("latitud")
        lng = data.get("longitud")

        if lat is not None and lng is not None:
            coordenada = Coordenada.objects.create(latitud=lat, longitud=lng)
            return JsonResponse({"mensaje": "Coordenada guardada", "id": coordenada.id}, status=201)
        return JsonResponse({"error": "Datos inválidos"}, status=400)

    return JsonResponse({"error": "Método no permitido"}, status=405)

def index(request):
    global comunas
    return render(request, "home.html", context= comunas)

def goto(request):
    global comunas
    comuna = request.POST.get("comuna")
    
    if int(comuna)-1<len(comunas['Comunas']):
        comuna = comunas['Comunas'][int(comuna)-1]
        nombre = comuna['nombre']
        inf_der = float(comuna['coords'][0][1:]),float(comuna['coords'][1][:-1])
        sup_izq = float(comuna['coords'][2][1:]),float(comuna['coords'][3][:-1])
    else:
        raise IndexError
    if "densidad" in request.POST:
        if os.path.exists(f'/home/winkrobed/Proyecto_Tecno/DJANGOUNCHAINED/polls/templates/mapa_calor_{nombre}.html'):
            return render(request, f'mapa_calor_{nombre}.html')
        else:
            map_maker(inf_der,sup_izq, nombre)
            if os.path.exists(f'/home/winkrobed/Proyecto_Tecno/DJANGOUNCHAINED/polls/templates/mapa_calor_{nombre}.html'):
                return render(request, f'mapa_calor_{nombre}.html')
            else:
                time.sleep(1)
                return render(request, f'mapa_calor_{nombre}.html')
    if "eod" in request.POST:
        if os.path.exists(f'/home/winkrobed/Proyecto_Tecno/DJANGOUNCHAINED/polls/templates/mapa_calor-EOD_{nombre}.html'):
            return render(request, f'mapa_calor-EOD_{nombre}.html')
        else:
            map_maker_eod(inf_der,sup_izq,nombre)
            if os.path.exists(f'/home/winkrobed/Proyecto_Tecno/DJANGOUNCHAINED/polls/templates/mapa_calor-EOD_{nombre}.html'):
                return render(request, f'mapa_calor-EOD_{nombre}.html')
            else:
                time.sleep(1)
                return render(request, f'mapa_calor-EOD_{nombre}.html')
 
    
def map_view(request):

    return render(request, 'map.html')

