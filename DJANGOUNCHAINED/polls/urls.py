from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("goto", views.goto, name="goto"),
    path("mapa", views.map_view, name="mapa"),
    path('guardar-coordenadas/', views.guardar_coordenadas, name='guardar_coordenadas'),
    path('form', views.formulario_view, name='formulario')
]