import datetime
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Q
from numpy import NaN
import pandas as pd
from django.db.models import Sum
from django.core.paginator import Paginator, Page
from django.db.utils import DataError


from .models import Country_meta, HS_Code_meta, TradeData,  Unit_meta
from .forms import UploadCountryMetaForm, UploadHSCodeMetaForm, UploadTradeDataForm, UploadUnitMetaForm

tables =[
    {
        "name":"Forest Data",
        "url":"forest_table"
    }
    # {
    #     "name":"Population Data",
    #     "url":"#"
    # },
    # {
    #     "name":"Mining Data",
    #     "url":"#"
    # },
    # {
    #     "name":"Land Data",
    #     "url":"#"
    # },
    # {
    #     "name":"Hotel Data",
    #     "url":"#"
    # },
    # {
    #     "name":"Tourism Data",
    #     "url":"#"
    # },
    # {
    #     "name":"Transport Data",
    #     "url":"#"
    # },
    # {
    #     "name":"water Data",
    #     "url":"#"
    # },
    # {
    #     "name":"Forest Data",
    #     "url":"#"
    # },
    # {
    #     "name":"Educational Data",
    #     "url":"#"
    # },
    ]

def is_valid_queryparam(param):
    return param !='' and param is not None


def display_trade_table(request):
    data = TradeData.objects.all()
    country_categories = Country_meta.objects.all()
    unit_categories = Unit_meta.objects.all()
    hs_codes = HS_Code_meta.objects.all()
    trade_type_categories = [choice[1] for choice in TradeData.TRADE_OPTIONS]

    currency_product_originDestination_query = request.GET.get('currency_product_originDestination')
    quantity_min = request.GET.get('quantity_min')
    quantity_max = request.GET.get('quantity_max')
    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    country_category = request.GET.get('country_category')
    unit_category = request.GET.get('unit_category')
    hs_code = request.GET.get('hs_code')
    trade_type = request.GET.get('trade_type')

    if is_valid_queryparam(currency_product_originDestination_query):
        data = data.filter(
            Q(Currency_Type__icontains = currency_product_originDestination_query)  | Q(Origin_Destination__icontains = currency_product_originDestination_query) ).distinct()
        
    if is_valid_queryparam(quantity_min):
        data = data.filter(Quantity__gte=quantity_min)

    if is_valid_queryparam(quantity_max):
        data = data.filter(Quantity__lt=quantity_max)
 
    if is_valid_queryparam(date_min):
        data = data.filter(Calender__gte = date_min)

    if is_valid_queryparam(date_max):
        data = data.filter(Calender__lt = date_max)

    if is_valid_queryparam(country_category) and country_category != '--':
        data = data.filter(Origin_Destination_id=country_category)
    
    if is_valid_queryparam(unit_category) and unit_category != '--':
        data = data.filter(Unit=unit_category)

    if is_valid_queryparam(hs_code) and hs_code != '--':
        data = data.filter(HS_Code=hs_code)

    if is_valid_queryparam(trade_type) and trade_type != '--':
        data = data.filter(Trade_Type=trade_type) 

    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    
    context = { 'data_len': len(data), 'country_categories': country_categories, 'unit_categories': unit_categories,
               'hs_codes': hs_codes, 'page':page,'trade_type_categories': trade_type_categories , 'query_len': len(page), 'tables':tables}

    return render(request, 'trade_data/display_trade_table.html', context)

def upload_country_meta_excel(request):
    errors = [] 
    if request.method == 'POST':
        form = UploadCountryMetaForm(request.POST, request.FILES)
        if form.is_valid():
            excel_data = request.FILES['country_meta_file']

            # Read existing data from the database
            db_data_list = list(Country_meta.objects.values('Country_Name', 'Country_Code_2', 'Country_Code_3'))
            
            df = pd.read_excel(excel_data)
            df.replace( NaN, 'nan', inplace=True)

            # records_to_insert = []
            for index, row in df.iterrows():
                country_data = {
                    'Country_Name': row['Country_Name'],
                    'Country_Code_2': row['Country_Code_2'],
                    'Country_Code_3': row['Country_Code_3']
                }

                # Check for duplicates
                is_duplicate = country_data in db_data_list

                if not is_duplicate:
                    # Insert the non-duplicate record
                    try:
                        country_meta = Country_meta(**country_data)
                        country_meta.save()
                    except IntegrityError as e:
                        print(f"Error inserting row {index}: {e}")
                        print(f"Problematic row data: {country_data}")
                else:
                    errors.append(f"Could not add duplicate row {index}: {country_data}")
            if errors:
                # If there are errors, return them as a response
                return render(request, 'trade_data/error_template.html', {'errors': errors})
            else:
                return HttpResponse('success')
    else:
        form = UploadCountryMetaForm()
    return render(request, 'trade_data/upload_form.html', {'form': form, 'tables':tables})


def upload_unit_meta_excel(request):
    errors = [] 
    if request.method == 'POST':
        form = UploadUnitMetaForm(request.POST, request.FILES)
        if form.is_valid():
            excel_data = request.FILES['unit_meta_file']
            db_data_list = list(Unit_meta.objects.values('Unit_Code', 'Unit_Name'))

            df = pd.read_excel(excel_data)
            df.replace( NaN, 'nan', inplace=True)

            for index, row in df.iterrows():
                unit_data = {
                    'Unit_Name': row['Unit_Name'],
                    'Unit_Code': row['Unit_Code'],
                }
                is_duplicate = unit_data in db_data_list

                if not is_duplicate:
                    # Insert the non-duplicate record
                    try:
                        unit_meta = Unit_meta(**unit_data)
                        unit_meta.save()
                    except IntegrityError as e:
                        print(f"Error inserting row {index}: {e}")
                        print(f"Problematic row data: {unit_data}")
                else:
                    errors.append(f"Could not add duplicate row {index}: {unit_data}")
            if errors:
                # If there are errors, return them as a response
                return render(request, 'trade_data/error_template.html', {'errors': errors})
            else:
                return HttpResponse('success')
    else:
        form = UploadUnitMetaForm()
    return render(request, 'trade_data/upload_form.html', {'form': form, 'tables':tables})


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
    return render(request, 'trade_data/upload_form.html', {'form': form, 'tables':tables})

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

                except DataError as e:
                    print(f"Error inserting row {index}: {e}")
                    print(f"Problematic row data: {row}")

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

    return render(request, 'trade_data/upload_form.html', {'form': form, 'tables':tables})


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
    
def find_hs_code(hs_code):
    if hs_code == '--':
        return("All Commodities")
    else:
        hs_codes = HS_Code_meta.objects.all()
        hs_code_instance = hs_codes.filter(id = hs_code).first()
        if hs_code_instance:
            hs_code_instance = hs_code_instance.HS_Code + ' - ' + hs_code_instance.Product_Information
        else:
            hs_code_instance = 'All Commodities'
        return hs_code_instance

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
    display_hs_code = find_hs_code(hs_code)

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

# ********************Find total amount of each year*******************
    total_amount_year = data.values(
        'Calender__year'
    ).annotate(
        total_amount = Sum('Amount')
    )

    total_amount_year = total_amount_year.order_by('-Calender__year')
# *******************************************************************
    
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
               'years':sorted_years, 'display_country':display_country, 'display_hs_code':display_hs_code, 'queryset_length':len(total_amount_by_origin_destination), 'total_amount_year':total_amount_year, 'tables':tables}

    return render(request, 'trade_data/time_series.html', context)

