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
class UploadHotelDataForm(forms.Form):
    Hotel_data_file = forms.FileField()


class UploadHotelData(ModelForm):
    class Meta:
        model = Hotel
        fields='__all__'


# Land Data
class UploadLandDataForm(forms.Form):
    Land_data_file = forms.FileField()


class UploadLandData(ModelForm):
    class Meta:
        model = Land
        fields='__all__'

class UploadLandMetaForm(forms.Form):
    meta_file = forms.FileField()

# Population Data
class UploadPopulationDataForm(forms.Form):
    population_data_file = forms.FileField()


class UploadPopulationData(ModelForm):
    class Meta:
        model = PopulationData
        fields='__all__'


# water
class UploadWaterDataForm(forms.Form):
    Water_data_file = forms.FileField()


class UploadWaterData(ModelForm):
    class Meta:
        model = Water 
        fields='__all__'

class UploadWaterMetaForm(forms.Form):
    meta_file = forms.FileField()

# Tourism data
class UploadTourismDataForm(forms.Form):
    Tourism_data_file = forms.FileField()


class UploadTourismData(ModelForm):
    class Meta:
        model = Tourism
        fields='__all__'

class UploadTourismMetaForm(forms.Form):
    meta_file = forms.FileField()

# transport data
class UploadTransportDataForm(forms.Form):
    Transport_data_file = forms.FileField()


class UploadTransportData(ModelForm):
    class Meta:
        model = Transport
        fields='__all__'

class UploadTransportMetaForm(forms.Form):
    meta_file = forms.FileField()
