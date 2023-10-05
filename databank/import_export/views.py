from django import apps
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .forms import UploadTradeForm
from .models import HS_Code_meta, TradeData, Country_meta, TradersName_ExporterImporter_meta, Unit_meta
import pandas as pd


def display_table(request):
    # data = TradeData.objects.all()
    # return render(request, 'import_export/display_table.html', {'data': data })
    data = TradeData.objects.all()
    title_contains_query = request.GET.get('title_contains')
    title_or_author_query = request.GET.get('title_or_author')

    if title_contains_query !='' and title_contains_query is not None:
        data = data.filter(Currency_Type__icontains= title_contains_query)

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
        

