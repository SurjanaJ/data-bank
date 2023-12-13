from django import forms
from django.forms import ModelForm
from .models import ForestData,Hotel,Tourism,Transport,PopulationData,Water,Land

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

# Hotel Data

class UploadHotelData(ModelForm):
    class Meta:
        model = Hotel
        fields='__all__'


# Land Data

class UploadLandData(ModelForm):
    class Meta:
        model = Land
        fields='__all__'

# Population Data

class UploadPopulationData(ModelForm):
    class Meta:
        model = PopulationData
        fields='__all__'


# water

class UploadWaterData(ModelForm):
    class Meta:
        model = Water 
        fields='__all__'

# Tourism data

class UploadTourismData(ModelForm):
    class Meta:
        model = Tourism
        fields='__all__'

# transport data

class UploadTransportData(ModelForm):
    class Meta:
        model = Transport
        fields='__all__'


