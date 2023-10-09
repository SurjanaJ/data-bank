from django.http import HttpResponse
from django.shortcuts import render
import pandas as pd

from .models import Country_meta, HS_Code_meta,  Unit_meta
from .forms import UploadCountryMetaForm, UploadHSCodeMetaForm, UploadUnitMetaForm

# Create your views here.
def display_trade_table(request):
    return render(request,'import/display_trade_table.html')

def upload_country_meta_excel(request):
    if request.method =='POST':
        form = UploadCountryMetaForm(request.POST, request.FILES)
        if form.is_valid():
            excel_data = request.FILES['country_meta_file']
            df = pd.read_excel(excel_data)

            for index,row in df.iterrows():
                country_meta = Country_meta(
                    Country_Name = row['Country_Name'],
                    Country_Code_2 = row['Country_Code_2'],
                    Country_Code_3 =row['Country_Code_3']
                )

                country_meta.save()

            return HttpResponse('success')
    else:
        form = UploadCountryMetaForm()
    return render(request, 'import/upload_form.html', {'form':form})

def upload_unit_meta_excel(request):
    if request.method =='POST':
        form = UploadUnitMetaForm(request.POST, request.FILES)
        if form.is_valid():
            excel_data = request.FILES['unit_meta_file']
            df = pd.read_excel(excel_data)

            for index,row in df.iterrows():
                unit_meta = Unit_meta(
                    Unit_Code = row['Unit_Code'],
                    Unit_Name = row['Unit_Name']
                )

                unit_meta.save()

            return HttpResponse('success')
    else:
        form = UploadUnitMetaForm()
    return render(request, 'import/upload_form.html', {'form':form})

def upload_hs_code_meta_excel(request):
    if request.method =='POST':
        form = UploadHSCodeMetaForm(request.POST, request.FILES)
        if form.is_valid():
            excel_data = request.FILES['hs_code_meta_file']
            df = pd.read_excel(excel_data)

            for index,row in df.iterrows():
                hs_code_meta = HS_Code_meta(
                    HS_Code = row['HS_Code'],
                    Product_Information = row['Product_Information']
                )

                hs_code_meta.save()

            return HttpResponse('success')
    else:
        form = UploadHSCodeMetaForm()
    return render(request, 'import/upload_form.html', {'form':form})

# def upload_trade_excel(request):
#     if request.method == 'POST':
#         form = UploadTradeDataForm(request.POST, request.FILES )
#         if form.is_valid():
#             excel_data = request.FILES['tradeData_file']
#             df = pd.read_excel(excel_data)

#             for index, row in df.iterrows():
#                 Country = row['Country']
#                 HS_Code = row['HS_Code']
#                 Unit = row['Unit']
#                 Origin_Destination = row['Origin_Destination']

#                 try:
#                     Country = Country_meta.objects.get(Country_Name=Country)
#                     HS_Code = HS_Code_meta.objects.get(HS_Code= HS_Code)
#                     Unit = Unit_meta.objects.get(Unit_Name = Unit)
#                     Origin_Destination = Country_meta.objects.get(Country_Name = Origin_Destination)
                
#                 except (Country_meta.DoesNotExist and HS_Code_meta.DoesNotExist  and Unit_meta.DoesNotExist ):
#                     return HttpResponse('could not upload the file.')

#                 # Create a TradeData instance and set the 'Country_Name' field
#                 trade_data = TradeData(
#                     Trade_Type=row['Trade_Type'],
#                     Calender = row['Calender'],
#                     Fiscal_Year = row['Fiscal_Year'],
#                     Month_Duration = row['Month_Duration'],
#                     Country=Country,
#                     HS_Code=HS_Code,
#                     Unit=Unit,
#                     Quantity=row['Quantity'],
#                     Currency_Type = row['Currency_Type'],
#                     Amount =row['Amount'],
#                     Tarrif= row['Tarrif'],
#                     Origin_Destination= Origin_Destination,
#                     TradersName_ExporterImporter = row['TradersName_ExporterImporter'],
#                     DocumentsLegalProcedural = row['DocumentsLegalProcedural'],
#                     Product_Information = row['Product_Information'],
#                 )
#                 trade_data.save()
        
#             return HttpResponse('success')

#     else:
#         form= UploadTradeDataForm()

#     return render(request, 'import/upload_form.html', {'form':form})
        
