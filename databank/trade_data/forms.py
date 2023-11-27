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