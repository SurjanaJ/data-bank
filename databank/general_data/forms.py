from django import forms
from django.forms import ModelForm
from .models import Crime, Education, ForestData,Hotel, Occupation, Services,Tourism,Transport,PopulationData,Water,Land,Public_Unitillity

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

# public unitillity data
class UploadPublicUnitillityDataForm(forms.Form):
    Public_Unitillity_data_file = forms.FileField()


class UploadPublicUnitillityData(ModelForm):
    class Meta:
        model = Public_Unitillity
        fields='__all__'
# SERVICE DATA
class UploadServicesMetaForm(forms.Form):
    meta_file = forms.FileField()

class UploadServicesForm(forms.Form):
    file = forms.FileField()


class UpdateServices(ModelForm):
    class Meta:
        model = Services
        fields='__all__'

        widgets={
            'Country': forms.Select(attrs={'class': 'form-control '}),
            'Year': forms.DateInput(attrs={'class': 'form-control '}),
            'Direction': forms.Select(attrs={'class': 'form-control  '}),
            'Code': forms.Select(attrs={'class': 'form-control  '}),
            'Value': forms.NumberInput(attrs={'class': 'form-control  '}),
            'Origin Destination': forms.Select(attrs={'class': 'form-control '}),
        }

# CRIME DATA
class UploadCrimeMetaForm(forms.Form):
    meta_file = forms.FileField()

class UploadCrimeForm(forms.Form):
    file = forms.FileField()

class UpdateCrime(ModelForm):
    class Meta:
        model = Crime
        fields='__all__'

        widgets={
            'Country': forms.Select(attrs={'class': 'form-control '}),
            'Year': forms.DateInput(attrs={'class': 'form-control '}),
            'Gender': forms.Select(attrs={'class': 'form-control  '}),
            'Code': forms.Select(attrs={'class': 'form-control  '}),
            'Age': forms.NumberInput(attrs={'class': 'form-control  '}),
            'District': forms.TextInput(attrs={'class': 'form-control '}),
        }

# EDUCATION DATA
class UploadEducationLevelMetaForm(forms.Form):
    meta_file = forms.FileField()

class UploadEducationDegreeMetaForm(forms.Form):
    meta_file = forms.FileField()

class UploadEducationForm(forms.Form):
    file = forms.FileField()

class UpdateEducation(ModelForm):
    class Meta:
        model = Education
        fields='__all__'

        widgets={
            'Level_Code': forms.Select(attrs={'class': 'form-control '}),
            'Degree_Code': forms.Select(attrs={'class': 'form-control  '}),
            'Male': forms.NumberInput(attrs={'class': 'form-control  '}),
            'Female': forms.NumberInput(attrs={'class': 'form-control  '}),
            'District': forms.TextInput(attrs={'class': 'form-control '}),
        }

# OCCUPATION DATA
class UploadOccupationMetaForm(forms.Form):
    meta_file = forms.FileField()
    
class UploadOccupationForm(forms.Form):
    file = forms.FileField()

class UpdateOccupation(ModelForm):
    class Meta:
        model = Occupation
        fields='__all__'

        widgets={
            'Country': forms.Select(attrs={'class': 'form-control '}),
            'Year': forms.NumberInput(attrs={'class': 'form-control  '}),
            'Code': forms.Select(attrs={'class': 'form-control  '}),
            'Number': forms.NumberInput(attrs={'class': 'form-control  '}),
        }