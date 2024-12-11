from django.http import HttpResponse
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
import time
import sys
import os
import yaml
path = os.path.abspath(r"")
print(path)
from app_testing.src.mapmakereodtest import map_maker_eod
from app_testing.src.mapmakertest import map_maker
pato = path

comunas = yaml.safe_load(open(f'{pato}/data/poligonos_comuna.yml','r'))
from .forms import CoordenadasForm
import json

def formulario_view(request):
    if request.method == "POST":
        form = CoordenadasForm(request.POST)
        if form.is_valid():
            latitud = form.cleaned_data['latitud']
            longitud = form.cleaned_data['longitud']
            estructura = form.cleaned_data['estructura']
            capacidad = form.cleaned_data['capacidad']
            # Aquí puedes manejar las coordenadas, como guardarlas en la base de datos
            return HttpResponse(f"Coordenadas recibidas: Latitud {latitud}, Longitud {longitud}, Estructura {estructura}, Capacidad {capacidad}")
    else:
        form = CoordenadasForm()
    return render(request, 'formulario.html', {'form': form})

def home(request):
    if request.method =="POST":
        if 'mapa' in request.POST:
            form = CoordenadasForm()
            return render(request, "formulario.html", {'form': form})
        else:
            global comunas
            return render(request,"home.html",context= comunas)
    else:
        return render(request, "index.html")
    

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
        if os.path.exists(f'{pato}/DJANGOUNCHAINED/polls/templates/mapa_calor_{nombre}.html'):
            return render(request, f'mapa_calor_{nombre}.html')
        else:
            map_maker(inf_der,sup_izq, nombre)
            if os.path.exists(f'{pato}/DJANGOUNCHAINED/polls/templates/mapa_calor_{nombre}.html'):
                return render(request, f'mapa_calor_{nombre}.html')
            else:
                time.sleep(1)
                return render(request, f'mapa_calor_{nombre}.html')
    if "eod" in request.POST:
        if os.path.exists(f'{pato}/DJANGOUNCHAINED/polls/templates/mapa_calor-EOD_{nombre}.html'):
            return render(request, f'mapa_calor-EOD_{nombre}.html')
        else:
            map_maker_eod(inf_der,sup_izq,nombre)
            if os.path.exists(f'{pato}/DJANGOUNCHAINED/polls/templates/mapa_calor-EOD_{nombre}.html'):
                return render(request, f'mapa_calor-EOD_{nombre}.html')
            else:
                time.sleep(1)
                return render(request, f'mapa_calor-EOD_{nombre}.html')
 
    


