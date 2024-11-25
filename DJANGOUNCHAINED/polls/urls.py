from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("EOD", views.eod, name="eod"),
    path("density", views.densidad, name="pob"),
    path("goto", views.goto, name="goto"),
]