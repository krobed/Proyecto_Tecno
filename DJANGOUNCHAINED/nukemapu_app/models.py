from django.db import models


# Create your models here.

class Coordenada(models.Model):
    latitud = models.FloatField()
    longitud = models.FloatField()
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Lat: {self.latitud}, Lng: {self.longitud}"
