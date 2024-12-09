from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("goto", views.goto, name="goto"),
    path('form', views.formulario_view, name='formulario')
]