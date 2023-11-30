from django import forms
from django.forms import ModelForm
from .models import TradeData


class UploadCountryMetaForm(forms.Form):
    country_meta_file = forms.FileField()

class UploadUnitMetaForm(forms.Form):
    unit_meta_file = forms.FileField()

class UploadHSCodeMetaForm(forms.Form):
    hs_code_meta_file = forms.FileField()

class UploadTradeDataForm(forms.Form):
    trade_data_file = forms.FileField()

class UploadTradeData(ModelForm):
    class Meta:
        model = TradeData
        fields = '__all__'
        widgets = {
            'Trade_Type': forms.Select(attrs={'class': 'form-control  '}),
            'Calender': forms.DateInput(attrs={'class': 'form-control '}),
            'Fiscal_Year': forms.TextInput(attrs={'class': 'form-control '}),
            'Duration': forms.TextInput(attrs={'class': 'form-control'}),
            'Country': forms.Select(attrs={'class': 'form-control'}),
            'HS_Code': forms.Select(attrs={'class': 'form-control'}),
            'Unit': forms.Select(attrs={'class': 'form-control'}),
            'Quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'Currency_Type': forms.TextInput(attrs={'class': 'form-control'}),
            'Amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'Tarrif': forms.NumberInput(attrs={'class': 'form-control'}),
            'Origin_Destination': forms.Select(attrs={'class': 'form-control'}),
            'TradersName_ExporterImporter': forms.TextInput(attrs={'class': 'form-control'}),
            'DocumentsLegalProcedural': forms.TextInput(attrs={'class': 'form-control'}),

            

            # Add more fields and widgets as needed
        }




