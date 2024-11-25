from django.http import HttpResponse
from django.shortcuts import render
import sys
sys.path.insert(1, '/home/winkrobed/Proyecto_Tecno/app-testing/test')
from mapmakereodtest import map_maker_eod
from mapmakertest import map_maker

comunas = {'San Miguel': [(-33.519007115903506, -70.63681595168819), 
                          (-33.47663483941321, -70.65475456613319)]}
comunas['Santiago Centro'] = [(-33.471068121121235, -70.62523235636876),
                              (-33.42701272190789, -70.67985587244763)]
comunas['Quinta Normal'] = [(-33.44432398486508, -70.67177893619858),
                            (-33.41130134710383, -70.72138907566847)]


def index(request):
    return render(request, "home.html")

def goto(request):
    global comunas
    comuna = request.POST.get("comuna")
    inf_der = comunas[comuna][0]
    sup_izq = comunas[comuna][1]
    if "densidad" in request.POST:
        map_maker(inf_der,sup_izq)
        return render(request, 'mapa_calor.html')
    if "eod" in request.POST:
        map_maker_eod(inf_der,sup_izq)
        return render(request, 'mapa_calor-EOD.html')
    
    
def densidad(request):
    return render(request, 'mapa_calor.html')
    
    


def eod(request):
    return render(request, 'mapa_calor-EOD.html')
    
    