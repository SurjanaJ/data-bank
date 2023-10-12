
import datetime
from django.http import HttpResponse
from django.shortcuts import render
import pandas as pd
from django.db.models import Sum

from .models import Country_meta, HS_Code_meta, TradeData,  Unit_meta
from .forms import UploadCountryMetaForm, UploadHSCodeMetaForm, UploadTradeDataForm, UploadUnitMetaForm

# Create your views here.

def is_valid_queryparam(param):
    return param !='' and param is not None
def display_trade_table(request):
    data = TradeData.objects.all()
    country_categories = Country_meta.objects.all()
    unit_categories = Unit_meta.objects.all()
    hs_codes = HS_Code_meta.objects.all()
    trade_type_categories = [choice[1] for choice in TradeData.TRADE_OPTIONS]

    country_category = request.GET.get('country_category')
    unit_category = request.GET.get('unit_category')
    hs_code = request.GET.get('hs_code')
    trade_type = request.GET.get('trade_type')

    context = {'data': data, 'country_categories': country_categories, 'unit_categories': unit_categories,
               'hs_codes': hs_codes, 'trade_type_categories': trade_type_categories}

    return render(request, 'import/display_trade_table.html', context)


def upload_country_meta_excel(request):
    if request.method == 'POST':
        form = UploadCountryMetaForm(request.POST, request.FILES)
        if form.is_valid():
            excel_data = request.FILES['country_meta_file']
            df = pd.read_excel(excel_data)

            for index, row in df.iterrows():
                country_meta = Country_meta(
                    Country_Name=row['Country_Name'],
                    Country_Code_2=row['Country_Code_2'],
                    Country_Code_3=row['Country_Code_3']
                )

                country_meta.save()

            return HttpResponse('success')
    else:
        form = UploadCountryMetaForm()
    return render(request, 'import/upload_form.html', {'form': form})


def upload_unit_meta_excel(request):
    if request.method == 'POST':
        form = UploadUnitMetaForm(request.POST, request.FILES)
        if form.is_valid():
            excel_data = request.FILES['unit_meta_file']
            df = pd.read_excel(excel_data)

            for index, row in df.iterrows():
                unit_meta = Unit_meta(
                    Unit_Code=row['Unit_Code'],
                    Unit_Name=row['Unit_Name']
                )

                unit_meta.save()

            return HttpResponse('success')
    else:
        form = UploadUnitMetaForm()
    return render(request, 'import/upload_form.html', {'form': form})


def upload_hs_code_meta_excel(request):
    if request.method == 'POST':
        form = UploadHSCodeMetaForm(request.POST, request.FILES)
        if form.is_valid():
            excel_data = request.FILES['hs_code_meta_file']
            df = pd.read_excel(excel_data)

            for index, row in df.iterrows():
                hs_code_meta = HS_Code_meta(
                    HS_Code=row['HS_Code'],
                    Product_Information=row['Product_Information']
                )

                hs_code_meta.save()

            return HttpResponse('success')
    else:
        form = UploadHSCodeMetaForm()
    return render(request, 'import/upload_form.html', {'form': form})


def upload_trade_excel(request):
    if request.method == 'POST':
        form = UploadTradeDataForm(request.POST, request.FILES)
        if form.is_valid():
            excel_data = request.FILES['trade_data_file']
            df = pd.read_excel(excel_data)

            for index, row in df.iterrows():
                Country = row['Country']
                HS_Code = row['HS_Code']
                Unit = row['Unit']
                Origin_Destination = row['Origin_Destination']
                Calender = row['Calender']

                try:
                    Country = Country_meta.objects.get(Country_Name=Country)
                    HS_Code = HS_Code_meta.objects.get(HS_Code=HS_Code)
                    Unit = Unit_meta.objects.get(Unit_Code=Unit)
                    Origin_Destination = Country_meta.objects.get(
                        Country_Name=Origin_Destination)

                except (Country_meta.DoesNotExist, HS_Code_meta.DoesNotExist, Unit_meta.DoesNotExist):
                    return HttpResponse('could not upload the file.')

                trade_data = TradeData(
                    Trade_Type=row['Trade_Type'],
                    Calender=datetime.date(Calender, 1, 1),
                    Fiscal_Year=row['Fiscal_Year'],
                    Duration=row['Duration'],
                    Country=Country,
                    HS_Code=HS_Code,
                    Unit=Unit,
                    Quantity=row['Quantity'],
                    Currency_Type=row['Currency_Type'],
                    Amount=row['Amount'],
                    Tarrif=row['Tarrif'],
                    Origin_Destination=Origin_Destination,
                    TradersName_ExporterImporter=row['TradersName_ExporterImporter'],
                    DocumentsLegalProcedural=row['DocumentsLegalProcedural']
                )
                trade_data.save()

            return HttpResponse('success')

    else:
        form = UploadTradeDataForm()

    return render(request, 'import/upload_form.html', {'form': form})


def find_country_name(country_category):
    if country_category == '--':
        return('All Countries')
    else:
        country_categories = Country_meta.objects.all()
        country_instance = country_categories.filter(id  = country_category).first()
        if country_instance:
            country_instance = country_instance.Country_Name
        else:
            country_instance = 'All Countries'
        return country_instance

def time_series_analysis(request):
    # Filter categories
    data = TradeData.objects.all()
    country_categories = Country_meta.objects.all()
    unit_categories = Unit_meta.objects.all()
    hs_codes = HS_Code_meta.objects.all()
    trade_type_categories = [choice[1] for choice in TradeData.TRADE_OPTIONS]

# get filter categories set by user
    country_category = request.GET.get('country_category')
    hs_code = request.GET.get('hs_code')
    trade_type = request.GET.get('trade_type')

    display_country = find_country_name(country_category)
    

    if is_valid_queryparam(country_category) and country_category != '--':
        data = data.filter(Origin_Destination_id=country_category)

    if is_valid_queryparam(hs_code) and hs_code != '--':
        data = data.filter(HS_Code_id=hs_code)

    if is_valid_queryparam(trade_type) and trade_type != '--':
        data = data.filter(Trade_Type=trade_type)

    # Group by Origin_Destination and year, and calculate the total amount
    total_amount_by_origin_destination = data.values(
        'Origin_Destination__Country_Name',
        'HS_Code_id__HS_Code',
        'Calender__year',
    ).annotate(
        total_amount=Sum('Amount')
    )

    years = set()
    result_country = {}
    result_hs_code = {}

    for item in total_amount_by_origin_destination:
        year = item['Calender__year']
        years.add(year)

    for item in total_amount_by_origin_destination:
        origin_destination = item['Origin_Destination__Country_Name']
        hs_code = item['HS_Code_id__HS_Code']
        year = item['Calender__year']
        total_amount = item['total_amount']
        
        if origin_destination not in result_country:
            result_country[origin_destination] = {}
        
        if hs_code not in result_hs_code:
            result_hs_code[hs_code] = {}
        
        for y in years:
            result_country[origin_destination][y] = 0
            result_hs_code[hs_code][y] = 0
        
    
    for item in total_amount_by_origin_destination:
        origin_destination = item['Origin_Destination__Country_Name']
        hs_code = item['HS_Code_id__HS_Code']
        year = item['Calender__year']
        total_amount = item['total_amount']
        result_country[origin_destination][year] = total_amount
        result_hs_code[hs_code][year] =total_amount
        

    sorted_years = sorted(list(years), reverse=True)
    
    for origin_destination, year_data in result_country.items():
        result_country[origin_destination] = dict(
            sorted(year_data.items(), key=lambda x: x[0], reverse=True))
        
    for hs_code, year_data in result_hs_code.items():
        result_hs_code[hs_code] = dict(sorted(year_data.items(), key=lambda x: x[0], reverse=True))
        

    context = {'data':data, 'country_categories':country_categories, 'unit_categories':unit_categories,'hs_codes':hs_codes, 'trade_type_categories':trade_type_categories, 'result_country': result_country,'result_hs_code': result_hs_code,
               'years':sorted_years, 'display_country':display_country }

    return render(request, 'import/time_series.html', context)

