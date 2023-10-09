from django import forms
from django.forms import ModelForm


class UploadCountryMetaForm(forms.Form):
    country_meta_file = forms.FileField()

class UploadUnitMetaForm(forms.Form):
    unit_meta_file = forms.FileField()

class UploadHSCodeMetaForm(forms.Form):
    hs_code_meta_file = forms.FileField()
