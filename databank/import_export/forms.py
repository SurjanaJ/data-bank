from django import forms
from django.forms import ModelForm
from .models import Country_meta, TradeData

# class upload_country_Form(ModelForm):
#     excel_file = forms.FileField(required=False)
#     # class Meta:
#     #     model = Country_meta
#     #     fields = ['Country_Name','Country_Code_2','Country_Code_3']

#     def clean_excel_file(self):
#         excel_file = self.cleaned_data.get('excel_file')
#         if excel_file:
#             # Add validation for the Excel file if needed
#             # For example, you can check the file extension
#             allowed_extensions = ['.xls', '.xlsx']
#             file_extension = str(excel_file.name.split('.')[-1]).lower()
#             if file_extension not in allowed_extensions:
#                 raise forms.ValidationError("Invalid file type. Please upload a valid Excel file.")
#         return excel_file


class UploadTradeForm(forms.Form):
    trade_file = forms.FileField()

class UploadTradeData(ModelForm):
    class Meta:
        model = TradeData
        fields = '__all__'