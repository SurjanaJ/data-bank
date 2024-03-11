from django import forms
from django.forms import ModelForm
from .models import ActivityData,Climate_Data, Crime, Exchange,ForestData, Disaster_Data, Education, Health_disease,Road,Mining,Housing,Political_Data,Hotel, Occupation, Services,Tourism,Transport,PopulationData,Water,Land,Public_Unitillity
from .models import Climate_Data, Crime, Education, ForestData,Hotel, Occupation, Services,Tourism,Transport,PopulationData,Water,Land


from django.forms import ModelForm
from .models import Production,Budgetary_Data, Publication,Climate_Data,Index, Crime,ForestData, Disaster_Data, Education, Health_disease,Road,Mining,Housing,Political_Data,Hotel, Occupation, Services,Tourism,Transport,PopulationData,Water,Land,Public_Unitillity
from .models import Climate_Data, Crime, Education, Energy, Exchange, ForestData,Hotel, Occupation, Services,Tourism,Transport,PopulationData,Water,Land

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

class UpdateForest(ModelForm):
    class Meta:
        model = ForestData
        fields='__all__'

        widgets={
            'Country': forms.Select(attrs={'class': 'form-control '}),
            'Year': forms.DateInput(attrs={'class': 'form-control '}),
            'Name_Of_The_Plant': forms.TextInput(attrs={'class': 'form-control '}),
            'Scientific_Name': forms.TextInput(attrs={'class': 'form-control '}),
            'Local_Name': forms.TextInput(attrs={'class': 'form-control '}),
            'Stock_Unit': forms.Select(attrs={'class': 'form-control  '}),
            'Stock_Available': forms.NumberInput(attrs={'class': 'form-control  '}),
            'Area_Unit': forms.TextInput(attrs={'class': 'form-control '}),
            'Area_Covered': forms.NumberInput(attrs={'class': 'form-control '}),
        }

    def __init__(self, *args, **kwargs):
        super(UpdateForest, self).__init__(*args, **kwargs)

        # Set the labels
        self.fields['Name_Of_The_Plant'].label = 'Name Of The Plant'
        self.fields['Scientific_Name'].label = 'Scientific Name'
        self.fields['Local_Name'].label = 'Local Name'
        self.fields['Stock_Unit'].label = 'Stock Unit'
        self.fields['Stock_Available'].label = 'Stock Available'
        self.fields['Area_Unit'].label = 'Area Unit'
        self.fields['Area_Covered'].label = 'Area Covered'


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


class UpdatePopulation(ModelForm):
    class Meta:
        model = PopulationData
        fields='__all__'

        widgets={
            'Country': forms.Select(attrs={'class': 'form-control '}),
            'Year': forms.DateInput(attrs={'class': 'form-control '}),
            'Gender': forms.Select(attrs={'class': 'form-control  '}),
            'Age_Group': forms.Select(attrs={'class': 'form-control  '}),
            'Population': forms.NumberInput(attrs={'class': 'form-control  '}),
        }

    def __init__(self, *args, **kwargs):
        super(UpdatePopulation, self).__init__(*args, **kwargs)

        # Set the labels
        self.fields['Age_Group'].label = 'Age Group'


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
            'Code': forms.Select(attrs={'class': 'form-control'}),
            'Value': forms.NumberInput(attrs={'class': 'form-control'}),
            'Origin_Destination': forms.Select(attrs={'class': 'form-control'}),
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
            'Degree_Code': forms.Select(attrs={'class': 'form-control '}),
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


#disaster data
class UploadDisasterMetaForm(forms.Form):
    meta_file = forms.FileField()        


class UpdateDisaster(ModelForm):
    class Meta:
        model = Disaster_Data
        fields='__all__'

class UploadDisasterForm(forms.Form):
    file = forms.FileField()

#health disease 

class UploadHealthDiseaseMetaForm(forms.Form):
    meta_file = forms.FileField()        


class UpdateHealthDisease(ModelForm):
    class Meta:
        model = Health_disease
        fields='__all__'

class UploadHealthDiseaseForm(forms.Form):
    file = forms.FileField()

#Mining 
class UploadMiningMetaForm(forms.Form):
    meta_file = forms.FileField()        


class UpdateMining(ModelForm):
    class Meta:
        model = Mining
        fields='__all__'

class UploadMiningForm(forms.Form):
    file = forms.FileField()

#Housing
    
class UploadHousingMetaForm(forms.Form):
    meta_file = forms.FileField()        


class UpdateHousing(ModelForm):
    class Meta:
        model = Housing
        fields='__all__'

class UploadHousingForm(forms.Form):
    file = forms.FileField()

#political 

class UpdatePolitical(ModelForm):
    class Meta:
        model = Political_Data
        fields='__all__'

class UploadPoliticalForm(forms.Form):
    file = forms.FileField()

#activity
class UpdateActivity(ModelForm):
    class Meta:
        model = ActivityData
        fields='__all__'

class UploadActivityDataForm(forms.Form):
    file = forms.FileField()

class UploadActivityMetaForm(forms.Form):
    meta_file = forms.FileField() 
#Road

class UploadRoadMetaForm(forms.Form):
    meta_file = forms.FileField()        


class UpdateRoad(ModelForm):
    class Meta:
        model = Road
        fields='__all__'

class UploadRoadForm(forms.Form):
    file = forms.FileField()

# public unitillity data
class UploadPublicUnitillityDataForm(forms.Form):
    Public_Unitillity_data_file = forms.FileField()


class UploadPublicUnitillityData(ModelForm):
    class Meta:
        model = Public_Unitillity
        fields='__all__'

# CLIMATE DATA
class UploadClimatePlaceMeta(forms.Form):
    meta_file = forms.FileField()

class UploadClimateForm(forms.Form):
    file = forms.FileField()

class UpdateClimate(ModelForm):
    class Meta:
        model = Climate_Data
        fields='__all__'

        widgets={
            'Country': forms.Select(attrs={'class': 'form-control '}),
            'Date': forms.DateInput(attrs={'class': 'form-control '}),
            'Place': forms.Select(attrs={'class': 'form-control '}),
            'Temperature_Unit': forms.Select(attrs={'class': 'form-control '}),
            'Max_Temperature': forms.NumberInput(attrs={'class': 'form-control  '}),
            'Min_Temperature': forms.NumberInput(attrs={'class': 'form-control  '}),
            'Climate': forms.Select(attrs={'class': 'form-control '}),
            'Climate_Unit': forms.Select(attrs={'class': 'form-control '}),
            'Amount': forms.NumberInput(attrs={'class': 'form-control  '})
        }

# EXCHANGE DATA
class UploadCurrencyForm(forms.Form):
    meta_file = forms.FileField()  

class UploadExchangeForm(forms.Form):
    file = forms.FileField()     

class UpdateExchange(ModelForm):
    class Meta:
        model = Exchange
        fields='__all__'

        widgets={
            'Country': forms.Select(attrs={'class': 'form-control '}),
            'Currency': forms.Select(attrs={'class': 'form-control '}),
            'Selling': forms.NumberInput(attrs={'class': 'form-control '}),
            'Buying': forms.NumberInput(attrs={'class': 'form-control '}),
        }

    def __init__(self, *args, **kwargs):
        super(UpdateExchange, self).__init__(*args, **kwargs)

        # Set the label for 'Selling' field
        self.fields['Selling'].label = 'Selling Against USD'
        self.fields['Buying'].label = 'Buying Against USD'


# ENERGY_DATA
class UploadEnergyMetaForm(forms.Form):
    meta_file = forms.FileField()  

class UploadEnergyForm(forms.Form):
    file = forms.FileField() 

class UpdateEnergy(ModelForm):
    class Meta:
        model = Energy
        fields='__all__'

        widgets={
            'Year': forms.NumberInput(attrs={'class': 'form-control '}),
            'Country': forms.Select(attrs={'class': 'form-control '}),
            'Power_Code': forms.Select(attrs={'class': 'form-control '}),
            'Potential_Unit': forms.Select(attrs={'class': 'form-control '}),
            'Potential_Capacity_MW':forms.NumberInput(attrs={'class': 'form-control '}),
            'Unit_Production': forms.Select(attrs={'class': 'form-control '}),
            'Current_Production_In_MW':forms.NumberInput(attrs={'class': 'form-control '}),
            'Generating_Company':forms.TextInput(attrs={'class': 'form-control '})
        }

    def __init__(self, *args, **kwargs):
        super(UpdateEnergy, self).__init__(*args, **kwargs)

        # Set the label for 'Selling' field
        self.fields['Power_Code'].label = 'Power Code'
        self.fields['Potential_Unit'].label = 'Potential Unit'
        self.fields['Unit_Production'].label = 'Unit Production'
        self.fields['Potential_Capacity_MW'].label = 'Potential Capacity MW'
        self.fields['Current_Production_In_MW'].label = 'Current Production In MW'
        self.fields['Generating_Company'].label = 'Generating Company'


# INDEX_DATA
class UploadIndexForm(forms.Form):
    file = forms.FileField() 

class UpdateIndex(ModelForm):
    class Meta:
        model = Index
        fields='__all__'

        widgets={
            'Year': forms.NumberInput(attrs={'class': 'form-control '}),
            'Country': forms.Select(attrs={'class': 'form-control '}),
            'Index_Name': forms.TextInput(attrs={'class': 'form-control '}),
            'Score':forms.NumberInput(attrs={'class': 'form-control '}),
            'Rank':forms.NumberInput(attrs={'class': 'form-control '}),
            'No_Of_Countries': forms.NumberInput(attrs={'class': 'form-control '}),
        }

    def __init__(self, *args, **kwargs):
        super(UpdateIndex, self).__init__(*args, **kwargs)

        # Set the label for 'Selling' field
        self.fields['Index_Name'].label = 'Index Name'
        self.fields['No_Of_Countries'].label = 'No Of Countries'


# PUBLICATION DATA
class UploadPublicationForm(forms.Form):
    file = forms.FileField() 

class UpdatePublication(ModelForm):
    class Meta:
        model = Publication
        fields='__all__'

        widgets={
            'Year': forms.NumberInput(attrs={'class': 'form-control '}),
            'Country': forms.Select(attrs={'class': 'form-control '}),
            'Book_Name': forms.TextInput(attrs={'class': 'form-control '}),
            'Writer_Name': forms.TextInput(attrs={'class': 'form-control '}),
        }

    def __init__(self, *args, **kwargs):
        super(UpdatePublication, self).__init__(*args, **kwargs)

        # Set the labels
        self.fields['Book_Name'].label = 'Book Name'
        self.fields['Writer_Name'].label = 'Writer Name'


# BUDGETARY DATA
class UploadBudgetForm(forms.Form):
    file = forms.FileField() 

class UpdateBudget(ModelForm):
    class Meta:
        model = Budgetary_Data
        fields='__all__'

        widgets={
            'Fiscal_Year': forms.TextInput(attrs={'class': 'form-control '}),
            'Country': forms.Select(attrs={'class': 'form-control '}),
            'Amount_In_USD': forms.NumberInput(attrs={'class': 'form-control '}),
            'Prefered_Denomination': forms.TextInput(attrs={'class': 'form-control '}),
        }

    def __init__(self, *args, **kwargs):
        super(UpdateBudget, self).__init__(*args, **kwargs)

        # Set the labels
        self.fields['Fiscal_Year'].label = 'Fiscal Year'
        self.fields['Amount_In_USD'].label = 'Amount In USD'
        self.fields['Prefered_Denomination'].label = 'Prefered Denomination'



#PRODUCTION DATA
class UploadProductionMetaForm(forms.Form):
    meta_file = forms.FileField()

class UploadProductionForm(forms.Form):
    file = forms.FileField() 

class UpdateProduction(ModelForm):
    class Meta:
        model = Production
        fields='__all__'

        widgets={
            'Code': forms.Select(attrs={'class': 'form-control '}),
            'Producer_Name': forms.TextInput(attrs={'class': 'form-control '}),
            'Province': forms.TextInput(attrs={'class': 'form-control '}),
            'District': forms.TextInput(attrs={'class': 'form-control '}),
        }

    def __init__(self, *args, **kwargs):
        super(UpdateProduction, self).__init__(*args, **kwargs)

        # Set the labels
        self.fields['Producer_Name'].label = 'Producer Name'
