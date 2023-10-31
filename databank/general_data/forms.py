from django import forms
from django.forms import ModelForm

class UploadForestDataForm(forms.Form):
    forest_data_file = forms.FileField()