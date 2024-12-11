from django.urls import path
from . import views

urlpatterns = [
    path("", views.formulario_view, name="formulario"),
    path("goto", views.goto, name="goto"),
    path("index", views.index, name='index')
]