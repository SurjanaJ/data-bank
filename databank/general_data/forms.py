from django import forms
from django.forms import ModelForm
from .models import ForestData

class UploadForestDataForm(forms.Form):
    forest_data_file = forms.FileField()

class UploadForestData(ModelForm):
    class Meta:
        model = ForestData
        fields='__all__'


        widgets={
            'Year': forms.DateInput(attrs={'class': 'form-control '}),
            'Country': forms.Select(attrs={'class': 'form-control '}),
            'Name_Of_The_Plant': forms.TextInput(attrs={'class': 'form-control '}),
            'Scientific_Name': forms.TextInput(attrs={'class': 'form-control '}),
            'Local_Name': forms.TextInput(attrs={'class': 'form-control  '}),
            'Stock_Unit': forms.TextInput(attrs={'class': 'form-control  '}),
            'Stock_Available': forms.NumberInput(attrs={'class': 'form-control  '}),
            'Area_Unit': forms.Select(attrs={'class': 'form-control  '}),
            'Area_Covered': forms.NumberInput(attrs={'class': 'form-control  '}),

        }
