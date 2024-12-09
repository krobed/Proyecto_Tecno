from django import forms

class CoordenadasForm(forms.Form):
    latitud = forms.FloatField(widget=forms.HiddenInput())
    longitud = forms.FloatField(widget=forms.HiddenInput())