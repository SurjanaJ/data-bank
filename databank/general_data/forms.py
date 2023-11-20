from django import forms
from django.forms import ModelForm
from .models import ForestData

class UploadForestDataForm(forms.Form):
    forest_data_file = forms.FileField()

class UpdateForestData(ModelForm):
    class Meta:
        model = ForestData
        fields='__all__'