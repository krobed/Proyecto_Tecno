from django import forms

c= [("Edificio", "Edificio"),("Mall", "Mall"),("Restaurante", "Restaurante"),("Parque", "Parque")]

class CoordenadasForm(forms.Form):
    latitud = forms.FloatField(widget=forms.HiddenInput())
    longitud = forms.FloatField(widget=forms.HiddenInput())
    estructura = forms.ChoiceField(choices = c)
    capacidad = forms.IntegerField(max_value=5000)