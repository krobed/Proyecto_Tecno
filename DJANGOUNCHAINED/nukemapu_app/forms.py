from django import forms

c= [("Edificio", "Edificio"),("Mall", "Mall"),("Parque", "Parque")]

class CoordenadasForm(forms.Form):
    todos_los_marcadores = forms.CharField(widget=forms.HiddenInput(), required=False)
    estructura = forms.ChoiceField(choices = c)
    capacidad = forms.IntegerField(max_value=5000)