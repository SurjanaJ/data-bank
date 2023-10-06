from django import forms
from django.forms import ModelForm
from .models import Country_meta, TradeData

class UploadTradeForm(forms.Form):
    trade_file = forms.FileField()

class UploadTradeData(ModelForm):
    class Meta:
        model = TradeData
        fields = '__all__'