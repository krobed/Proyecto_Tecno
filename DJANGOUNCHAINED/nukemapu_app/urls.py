from django.urls import path
from . import views

urlpatterns = [
    path("mapa", views.formulario_view,name="mapa"),
    path("goto", views.goto, name="goto"),
    path("index", views.index, name='index'),
    path("", views.home, name="home")
]