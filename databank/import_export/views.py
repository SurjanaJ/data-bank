from django import apps
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.db.models import Q

from .forms import UploadTradeForm
from .models import HS_Code_meta, TradeData, Country_meta, TradersName_ExporterImporter_meta, Unit_meta
import pandas as pd


def is_valid_queryparam(param):
    return param !='' and param is not None

def display_table(request):
    data = TradeData.objects.all()
    currency_product_originDestination_query = request.GET.get('currency_product_originDestination')
    quantity_min = request.GET.get('quantity_min')
    quantity_max = request.GET.get('quantity_max')
    # date_min = request.GET.get(date_min)
    # date_max = request.GET.get(date_max)

    if is_valid_queryparam(currency_product_originDestination_query):
        data = data.filter(
            Q(Currency_Type__icontains = currency_product_originDestination_query) | Q(Product_Information__icontains = currency_product_originDestination_query) | Q(Origin_Destination__icontains = currency_product_originDestination_query) ).distinct()
        
    if is_valid_queryparam(quantity_min):
        data = data.filter(Quantity__gte=quantity_min)

    if is_valid_queryparam(quantity_max):
        data = data.filter(Quantity__lt=quantity_max)

    # if is_valid_queryparam(date_min):
    #     data = data.filter()

    context = {'data': data}
    return render(request, 'import_export/display_table.html', context)


def upload_trade_excel(request):
    if request.method == 'POST':
        form = UploadTradeForm(request.POST, request.FILES )
        if form.is_valid():
            excel_data = request.FILES['trade_file']
            df = pd.read_excel(excel_data)

            for index, row in df.iterrows():

                Country_Name = row['Country_Name']
                HS_Code = row['HS_Code']
                Unit = row['Unit']
                TradersName_ExporterImporter = row['TradersName_ExporterImporter']

                try:
                    Country_Name = Country_meta.objects.get(Country_Name=Country_Name)
                    HS_Code = HS_Code_meta.objects.get(HS_Code= HS_Code)
                    Unit = Unit_meta.objects.get(Unit_Name = Unit)
                    TradersName_ExporterImporter = TradersName_ExporterImporter_meta.objects.get(Name = TradersName_ExporterImporter)
                
                except (Country_meta.DoesNotExist and HS_Code_meta.DoesNotExist  and Unit_meta.DoesNotExist and TradersName_ExporterImporter_meta.DoesNotExist ):
                    return HttpResponse('could not upload the file.')

                # Create a TradeData instance and set the 'Country_Name' field
                trade_data = TradeData(
                    Trade_Type=row['Trade_Type'],
                    Calender = row['Calender'],
                    Fiscal_Year = row['Fiscal_Year'],
                    Duration = row['Duration'],
                    Country_Name=Country_Name,
                    HS_Code=HS_Code,
                    Unit=Unit,
                    Quantity=row['Quantity'],
                    Currency_Type = row['Currency_Type'],
                    Amount =row['Amount'],
                    Tarrif= row['Tarrif'],
                    Origin_Destination= row['Origin_Destination'],
                    TradersName_ExporterImporter = TradersName_ExporterImporter,
                    Documents = row['Documents'],
                    Product_Information = row['Product_Information'],
                )
                trade_data.save()
        
            return HttpResponse('success')

    else:
        form= UploadTradeForm()

    return render(request, 'import_export/upload.html', {'form':form})
        

