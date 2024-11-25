from django.http import HttpResponse
from django.shortcuts import render
import time
import sys
import os

sys.path.insert(1, '/home/winkrobed/Proyecto_Tecno/app-testing/test')
from mapmakereodtest import map_maker_eod
from mapmakertest import map_maker

comunas = {'Comunas':[
                {'nombre': 'SanMiguel', 
                    'coords': [(-33.519007115903506, -70.63681595168819), (-33.47663483941321, -70.65475456613319)]},
                {'nombre':'SantiagoCentro', 
                    'coords': [(-33.471068121121235, -70.62523235636876),(-33.42701272190789, -70.67985587244763)]},
                {'nombre': 'QuintaNormal',
                    'coords': [(-33.44432398486508, -70.67177893619858),(-33.41130134710383, -70.72138907566847)]}
                     ]
}


def index(request):
    global comunas
    return render(request, "home.html", context= comunas)

def goto(request):
    global comunas
    comuna = request.POST.get("comuna")
    for i in comunas['Comunas']:
        if i['nombre'] == comuna:
            inf_der = i['coords'][0]
            sup_izq = i['coords'][1]
            break
    if "densidad" in request.POST:
        if os.path.exists(f'/home/winkrobed/Proyecto_Tecno/DJANGOUNCHAINED/polls/templates/mapa_calor_{comuna}.html'):
            return render(request, f'mapa_calor_{comuna}.html')
        else:
            map_maker(inf_der,sup_izq, comuna)
            if os.path.exists(f'/home/winkrobed/Proyecto_Tecno/DJANGOUNCHAINED/polls/templates/mapa_calor_{comuna}.html'):
                return render(request, f'mapa_calor_{comuna}.html')
            else:
                time.sleep(1)
                return render(request, f'mapa_calor_{comuna}.html')
    if "eod" in request.POST:
        if os.path.exists(f'/home/winkrobed/Proyecto_Tecno/DJANGOUNCHAINED/polls/templates/mapa_calor-EOD_{comuna}.html'):
            return render(request, f'mapa_calor-EOD_{comuna}.html')
        else:
            map_maker_eod(inf_der,sup_izq,comuna)
            if os.path.exists(f'/home/winkrobed/Proyecto_Tecno/DJANGOUNCHAINED/polls/templates/mapa_calor-EOD_{comuna}.html'):
                return render(request, f'mapa_calor-EOD_{comuna}.html')
            else:
                time.sleep(1)
                return render(request, f'mapa_calor-EOD_{comuna}.html')
 
    
    