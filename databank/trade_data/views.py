from datetime import date
from io import BytesIO
from django.db.models import F, Q
import json
from math import isnan
from django.db import IntegrityError
from django.forms import model_to_dict
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render,get_object_or_404
from django.db.models import Q
from numpy import NaN
import pandas as pd
from django.db.models import Sum
from django.core.paginator import Paginator, Page
from django.db.utils import DataError
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.views.decorators.http import require_POST

from accounts.decorators import allowed_users

from .forms import UploadTradeData
from django.contrib.auth.decorators import login_required

from .models import Country_meta, HS_Code_meta, TradeData,  Unit_meta
from .forms import UploadCountryMetaForm, UploadHSCodeMetaForm, UploadTradeDataForm, UploadUnitMetaForm,UploadTradeData

tables =[
    {
        "name":"Forest Data",
        "url":"forest_table"    
    },

    {
        "name":"Population Data",
        "url":"population_table"    
    },
        {
        "name":"Land Data",
        "url":"land_table"    
    },
        {
        "name":"Transport Data",
        "url":"transport_table"    
    },
        {
        "name":"Hotel Data",
        "url":"hotel_table"    
    },
        {
        "name":"Water Data",
        "url":"water_table"    
    },
        {
        "name":"Tourism Data",
        "url":"tourism_table"    
    },
    {
        "name":"Services Data",
        "url":"services_table"    
    },
    {
        "name": "Education Data",
        "url": "education_table"
    }
    ,
    {
        "name": "Occupation Data",
        "url": "occupation_table"
    }
    ,
    {
        "name": "Climate Data",
        "url": "climate_table"
    }
    ,
    {
        "name": "Crime Data",
        "url": "crime_table"
    },
    {
        "name": "Exchange Data",
        "url": "exchange_table"
    },
    {
        "name": "Energy Data",
        "url": "energy_table"
    },
    {
        "name": "Disaster Data",
        "url": "disaster_table"
    },
    {
        "name": "Health Disease Data",
        "url": "health_disease_table"
    },
    {
        "name": "Public Unitillity Data",
        "url": "public_unitillity_table"
    },
    {
        "name": "Housing Data",
        "url": "housing_table"
    },
    {
        "name": "Mining Data",
        "url": "mining_table"
    },
    {
        "name": "Political Data",
        "url": "political_table"
    },
    {
        "name": "Population Data",
        "url": "population_table"
    },
    {
        "name": "Road Data",
        "url": "road_table"
    },
    {
        "name": "Water Data",
        "url": "water_table"
    },
    
    {
        "name": "Index Data",
        "url": "index_table"
    },
    {
        "name": "Publication Data",
        "url": "publication_table"
    },
    {
        "name": "Budgetary Data",
        "url": "budget_table"
    },
    {
        "name": "Production Data",
        "url": "production_table"
    },
    {
        "name": "Population Data",
        "url": "population_table"
    },
    {
        "name": "Activity Data",
        "url": "activity_table"
    },
    ]


meta_tables =[
    {
        "name":"HS Code Meta",
        "url":"hs_code",
        "upload_url": "upload_hs_code_meta_excel"    
    },
    {
        "name": "Country Meta",
        "url":"country",
        "upload_url": "upload_country_meta_excel"    
    },
     {
        "name": "Unit Meta",
        "url":"unit",
        "upload_url": "upload_unit_meta_excel" 
    }, 
    {
        "name" : "Land Meta",
        "url":"land_meta",
        "upload_url": "upload_land_meta_excel" 
    },
    {
        "name" : "Transport Meta",
        "url":"transport_meta",
        "upload_url": "upload_transport_meta_excel" 

    },
    {
        "name": "Water Meta",
        "url": "water_meta",
        "upload_url": "upload_water_meta_excel" 
    },
    {
        "name":"Tourism Meta",
        "url": "tourism_meta",
        "upload_url": "upload_tourism_meta_excel"  
    },
    {
        "name" : "Services Meta",
        "url": "services_meta",
        "upload_url": "upload_services_meta_excel"
    },
    {
        "name" : "Crime Meta",
        "url": "crime_meta",
        "upload_url": "upload_crime_meta_excel"
    },
    {
        "name":"Education Level Meta",
        "url": "education_level_meta",
        "upload_url":"upload_education_level_meta_excel"
    },
    {
        "name":"Education Degree Meta",
        "url": "education_degree_meta",
        "upload_url":"upload_education_degree_meta_excel"
    },
    {
        "name":"Occupation Meta",
        "url": "occupation_meta",
        "upload_url":"upload_occupation_meta_excel"
    },
    {
        "name":"Climate Places Meta",
        "url": "place_meta",
        "upload_url":"upload_climate_place_meta_excel"
    },
    {
        "name":"Currency Meta",
        "url": "currency_meta",
        "upload_url":"upload_currency_excel"
    },
    {
        "name":"Energy Meta",
        "url":"energy_meta",
        "upload_url":"upload_energy_meta_excel"
    },
    {
        "name":"Mining Meta",
        "url":"mine_meta",
        "upload_url":"upload_mining_meta_excel"
    },
    {
        "name":"Road Meta",
        "url":"road_meta",
        "upload_url":"upload_road_meta_excel"
    },
    {
        "name":"Housing Meta",
        "url":"housing_meta",
        "upload_url":"upload_housing_meta_excel"
    },
    {
        "name":"Health Disease Meta",
        "url":"health_disease_meta",
        "upload_url":"upload_health_disease_meta_excel"
    },
    {
        "name":"Disaster Meta",
        "url":"disaster_data_meta",
        "upload_url":"upload_disaster_data_meta_excel",
    },
    {
        "name":"Production Meta",
        "url":"production_meta",
        "upload_url":"upload_production_meta_excel"
    },
    
    {
        "name":"Activity Meta",
        "url":"activity_meta",
        "upload_url":"upload_activity_meta_excel"
    },
    ]

def strip_spaces(value):
    if isinstance(value, str):
        return value.strip()
    return value

def is_valid_queryparam(param):
    return param !='' and param is not None

@login_required(login_url = 'login')
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

    paginator = Paginator(data, 40)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    
    context = { 'data_len': len(data), 'country_categories': country_categories, 'unit_categories': unit_categories,
               'hs_codes': hs_codes, 'page':page,'trade_type_categories': trade_type_categories , 'query_len': len(page), 'tables':tables, 'meta_tables':meta_tables}

    return render(request, 'trade_data/display_trade_table.html', context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def upload_country_meta_excel(request):
    errors = []
    duplicate_data = []
    added_count = 0
    updated_count = 0

    if request.method == 'POST':
        form = UploadCountryMetaForm(request.POST, request.FILES)

        if form.is_valid():
            excel_data = request.FILES['country_meta_file']

            df = pd.read_excel(excel_data)
            df.replace(NaN, '', inplace=True)

            for index, row in df.iterrows():
                country_data = {
                    'Country_Name': row['Country_Name'],
                    'Country_Code_2': row['Country_Code_2'],
                    'Country_Code_3': row['Country_Code_3']
                }

                # Check for duplicates based on the 'Country_Name' column
                existing_record = Country_meta.objects.filter(Q(Country_Name=country_data['Country_Name'])).first()

                if existing_record:
                    # If a duplicate record is found, check if all columns are identical
                    if all(getattr(existing_record, key) == value for key, value in country_data.items()):
                        duplicate_data.append({'row_index': index, 'data': country_data})
                    else:
                        # Update the row with non-duplicate data
                        for key, value in country_data.items():
                            setattr(existing_record, key, value)
                        try:
                            existing_record.save()
                            updated_count += 1
                        except IntegrityError as e:
                            errors.append(f"Error updating row {index}: {e}")
                else:
                    # Insert the non-duplicate record
                    try:
                        country_meta = Country_meta(**country_data)
                        country_meta.save()
                        added_count += 1
                    except IntegrityError as e:
                        errors.append(f"Error inserting row {index}: {e}")

            if added_count > 0:
                messages.success(request, str(added_count) + ' records added.')
            
            if updated_count > 0:
                messages.info(request, str(updated_count) + ' records updated.')

            if errors:
                # If there are errors, return them as a response
                return render(request, 'trade_data/error_template.html', {'errors': errors})
            elif duplicate_data:
                request.session['duplicate_data'] = duplicate_data
                return render(request, 'trade_data/duplicate_template.html', {'duplicate_data': duplicate_data})
            else:
                return redirect('country')

    else:
        form = UploadCountryMetaForm()

    return render(request, 'trade_data/upload_form.html', {'form': form, 'tables': tables, 'meta_tables':meta_tables})

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def upload_unit_meta_excel(request):
    errors = [] 
    added_count = 0
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
                        added_count += 1 
                    except IntegrityError as e:
                        print(f"Error inserting row {index}: {e}")
                        print(f"Problematic row data: {unit_data}")
                else:
                    errors.append(f"Could not add duplicate row {index}: {unit_data}")
            if errors:
                # If there are errors, return them as a response
                return render(request, 'trade_data/error_template.html', {'errors': errors})
            else:
                messages.success(request, str(added_count) + ' records added.')
                return redirect('unit')
    else:
        form = UploadUnitMetaForm()
    return render(request, 'trade_data/upload_form.html', {'form': form, 'tables':tables, 'meta_tables':meta_tables})

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def upload_hs_code_meta_excel(request):
    errors = []
    duplicate_data = []
    added_count = 0
    updated_count = 0

    if request.method == 'POST':
        form = UploadHSCodeMetaForm(request.POST, request.FILES)

        if form.is_valid():
            excel_data = request.FILES['hs_code_meta_file']
            df = pd.read_excel(excel_data, dtype={'HS_Code': str})

            try:
                with transaction.atomic():
                    for index, row in df.iterrows():
                        data = {
                            'HS_Code': row['HS_Code'],
                            'Product_Information': row['Product_Information']
                        }

                        existing_record = HS_Code_meta.objects.filter(HS_Code=data['HS_Code']).first()

                        if existing_record:
                            if existing_record == HS_Code_meta(**data):
                                duplicate_data.append({'row_index': index, 'data': data})

                            else:
                                HS_Code_meta.objects.update_or_create(
                                    HS_Code=data['HS_Code'],
                                    defaults={'Product_Information': data['Product_Information']}
                                )
                                updated_count += 1


                        else:
                            HS_Code_meta.objects.create(**data)
                            added_count += 1


            except IntegrityError as e:
                errors.append(f"Error during database operation: {e}")

            messages.info(request, str(updated_count) + ' records updated.')
            messages.success(request, str(added_count) + ' records added.')
            if errors:
                # If there are errors, return them as a response
                return render(request, 'trade_data/error_template.html', {'errors': errors})
            elif duplicate_data:
                request.session['duplicate_data'] = duplicate_data
                return render(request, 'trade_data/duplicate_template.html', {'duplicate_data': duplicate_data})
            else:
                return redirect('hs_code')
    else:
        form = UploadHSCodeMetaForm()

    return render(request, 'trade_data/upload_form.html', {'form': form, 'meta_tables':meta_tables})

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def upload_trade_excel(request):
    errors = []
    duplicate_data = []
    added_count = 0
    updated_count = 0

    if request.method == 'POST':
        form = UploadTradeDataForm(request.POST, request.FILES)

        if form.is_valid():
            excel_data = request.FILES['trade_data_file']
            df = pd.read_excel(excel_data, dtype={'HS Code': str})
            df.fillna('', inplace=True)
            df = df.map(strip_spaces)
            
             # Check if required columns exist
            required_columns = ['Trade Type', 'Calender', 'Calender Year','Duration','Country','HS Code' ,'Product Information','Unit','Quantity','Currency Type','Amount','Tarrif','Origin Destination','TradersName ExporterImporter','Documents Legal Procedural']  # Add your required column names here
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                errors.append(f"Missing columns: {', '.join(missing_columns)}")
                return render(request,'general_data/invalid_upload.html', {'missing_columns': missing_columns, 'tables': tables, 'meta_tables': meta_tables,} )
            

            #update existing data
            if 'id' in df.columns:
                for index, row in df.iterrows():
                    id = row.get('id')
                    data = {
                    'Trade Type':row['Trade Type'],
                    'Calender': row['Calender'],
                    'Calender Year':row['Fiscal Year'],
                    'Duration':row['Duration'],
                    'Country' : row['Country'],
                    'HS Code' : row['HS Code'],
                    'Product Information': row['Product Information'],
                    'Unit' : row['Unit'],
                    'Quantity':row['Quantity'],
                    'Currency Type':row['Currency Type'],
                    'Amount':row['Amount'],
                    'Tarrif' : 0.0 if row['Tarrif'] == 'nan' or (row['Tarrif']== '') else row['Tarrif'],
                    'Origin Destination' : row['Origin Destination'],
                    'TradersName ExporterImporter':row['TradersName ExporterImporter'],
                    'Documents Legal Procedural':row['Documents Legal Procedural']
                    }

                    #get existing data
                    try:
                        trade_instance = TradeData.objects.get(id = id)
                        trade_data = data

                        # check if all meta values exist
                        try:
                            Country = Country_meta.objects.get(Country_Name=row['Country'])
                            HS_Code = HS_Code_meta.objects.get(HS_Code=row['HS Code'])
                            Unit = Unit_meta.objects.get(Unit_Code=row['Unit'])
                            Origin_Destination = Country_meta.objects.get(
                                Country_Name=row['Origin Destination'])
                            
                            trade_instance.Country = Country
                            trade_instance.HS_Code = HS_Code
                            trade_instance.Unit = Unit
                            trade_instance.Origin_Destination = Origin_Destination
                            trade_instance.Trade_Type =row ['Trade Type']
                            trade_instance.Calender= row['Calender']
                            trade_instance.Fiscal_Year= row['Fiscal Year']
                            trade_instance.Duration= row['Duration']
                            trade_instance.Quantity= row['Quantity']
                            trade_instance.Currency_Type= row['Currency Type']
                            trade_instance.Amount= row['Amount']
                            trade_instance.Tarrif= row['Tarrif']
                            trade_instance.TradersName_ExporterImporter= row['TradersName ExporterImporter']
                            trade_instance.DocumentsLegalProcedural= row['Documents Legal Procedural']

                            
                            trade_instance.save()
                            updated_count += 1

                        #meta data does not exist
                        except Exception as e:
                            trade_data = data
                            errors.append({'row_index': index, 'data': trade_data, 'reason': str(e)})
                            continue

                    #existing data not found
                    except Exception as e:
                        trade_data = data
                        errors.append({
                                        'row_index': index,
                                        'data': trade_data,
                                        'reason': f'Error inserting row {index}: {e}'
                                    })
                        continue
            else:
            # add new data
                for index, row in df.iterrows():
                    data = {
                    'Trade Type':row['Trade Type'],
                    'Calender': row['Calender'],
                    'Fiscal Year':row['Fiscal Year'],
                    'Duration':row['Duration'],
                    'Country' : row['Country'],
                    'HS Code' : row['HS Code'],
                    'Product Information': row['Product Information'],
                    'Unit' : row['Unit'],
                    'Quantity':row['Quantity'],
                    'Currency Type':row['Currency Type'],
                    'Amount':row['Amount'],
                    'Tarrif' : 0.0 if row['Tarrif'] == 'nan' or (row['Tarrif']== '') else row['Tarrif'],
                    'Origin Destination' : row['Origin Destination'],
                    'TradersName ExporterImporter':row['TradersName ExporterImporter'],
                    'Documents Legal Procedural':row['Documents Legal Procedural']
                    }    

                    # Check if meta values exist
                    try:
                        Country = Country_meta.objects.get(Country_Name=row['Country'])
                        HS_Code = HS_Code_meta.objects.get(HS_Code=row['HS Code'])
                        Unit = Unit_meta.objects.get(Unit_Code=row['Unit'])
                        Origin_Destination = Country_meta.objects.get(
                                Country_Name=row['Origin Destination'])
                            
                        trade_data = {
                            'Trade_Type': row['Trade Type'],
                            'Calender': row['Calender'],
                            'Fiscal_Year':row['Fiscal Year'],
                            'Duration': row['Duration'],
                            'Country': Country,
                            'HS_Code':HS_Code,
                            'Unit':Unit,
                            'Quantity':row['Quantity'],
                            'Currency_Type':row['Currency Type'],
                            'Amount': row['Amount'],
                            'Tarrif':row['Tarrif'],
                            'Origin_Destination':Origin_Destination,
                            'TradersName_ExporterImporter': row['TradersName ExporterImporter'],
                            'DocumentsLegalProcedural':row['Documents Legal Procedural']
                        }

                        existing_record = TradeData.objects.filter(
                            Q(Trade_Type = row['Trade Type'])
                            & Q(Calender = row['Calender'])
                            & Q(Fiscal_Year = row['Fiscal Year'])
                            & Q(Duration = row['Duration'])
                            & Q(Country = Country)
                            & Q(HS_Code = HS_Code)
                            & Q(Unit = Unit)
                            & Q(Quantity = row['Quantity'])
                            & Q(Currency_Type = row['Currency Type'])
                            & Q(Amount = row['Amount'])
                            & Q(Tarrif = row['Tarrif'])
                            & Q(Origin_Destination = Origin_Destination)
                            & Q(TradersName_ExporterImporter = row['TradersName ExporterImporter'])
                            & Q(DocumentsLegalProcedural = row['Documents Legal Procedural'])
                        ).first()


                        # show duplicate data
                        if existing_record:
                            trade_data = data
                            duplicate_data.append({
                                'row_index': index,
                                    'data': {key: str(value) for key, value in trade_data.items()}
                            })
                            continue
                        else:
                            #add new record
                            try:
                                tradeData = TradeData(**trade_data)
                                tradeData.save()
                                added_count += 1
                            except Exception as e:
                                errors.append(f"Error inserting row {index}: {e}")

                    #meta values does not exist
                    except Exception as e:
                        trade_data = data
                        errors.append({'row_index': index, 'data': trade_data, 'reason': str(e)})
                        continue


            if added_count > 0:
                messages.success(request, str(added_count) + ' records added.')
            
            if updated_count > 0:
                messages.info(request, str(updated_count) + ' records updated.')

            if errors:
                request.session['errors'] = errors
                return render(request, 'trade_data/error_template.html', {'errors': errors})
            
            elif duplicate_data:
                request.session['duplicate_data'] = duplicate_data
                return render(request, 'trade_data/duplicate_template.html', {'duplicate_data': duplicate_data})
                
            else:
                return redirect('display_trade_table')    
    else:
        form = UploadTradeDataForm()

    return render(request, 'trade_data/upload_form.html', {'form': form, 'tables':tables, 'meta_tables':meta_tables})

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def upload_trade_record(request):
    trade_type_categories = [choice[1] for choice in TradeData.TRADE_OPTIONS]

    form = UploadTradeData()
    
    if request.method == 'POST':

        form = UploadTradeData(request.POST)

        if form.is_valid():
            form.save()
            return redirect('display_trade_table')

    context={'form': form,'trade_type_categories': trade_type_categories, 'meta_tables':meta_tables}
    return render(request, 'trade_data/upload_form.html', context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def update_trade_record(request,pk):
    trade_record = TradeData.objects.get(id=pk)
    form = UploadTradeData(instance=trade_record)

    if request.method == 'POST':
        form = UploadTradeData(request.POST, instance=trade_record)
        if form.is_valid():
            form.save()
            return redirect('display_trade_table')
        
    context={'form':form, 'meta_tables':meta_tables}
    return render(request,'trade_data/update_trade_record.html',context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def update_selected_trade(request):
    selected_ids = request.POST.getlist('selected_items')
    if not selected_ids:
        messages.error(request, 'No items selected.')
        return redirect('display_trade_table')
    else:
        queryset = TradeData.objects.filter(id__in=selected_ids)
        queryset = queryset.annotate(
        country = F('Country__Country_Name'),
        hs_code = F('HS_Code__HS_Code'),
        Product_Information = F('HS_Code__Product_Information'),
        unit = F('Unit__Unit_Code'),
        origin_destination = F('Origin_Destination__Country_Name')
    )

    data = pd.DataFrame(list(queryset.values('id','Trade_Type','Calender','Fiscal_Year','Duration','country','hs_code','Product_Information', 'unit','Quantity','Currency_Type','Amount','Tarrif','origin_destination','TradersName_ExporterImporter','DocumentsLegalProcedural')))

    data.rename(columns={
                        'Trade_Type':'Trade Type',
                        'Fiscal_Year':'Fiscal Year',
                         'country':'Country',
                         'hs_code': 'HS Code',
                         'Product_Information':'Product Information',
                         'unit':'Unit',
                         'Currency_Type':'Currency Type',
                         'origin_destination':'Origin Destination',
                         'TradersName_ExporterImporter':'TradersName ExporterImporter',
                         'DocumentsLegalProcedural':'Documents Legal Procedural'
                         }, inplace=True)
    column_order = ['id','Trade Type','Calender','Fiscal Year','Duration','Country','HS Code', 'Product Information','Unit','Quantity','Currency Type','Amount','Tarrif','Origin Destination','TradersName ExporterImporter','Documents Legal Procedural']

    data = data[column_order]
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')  
    data.to_excel(writer, sheet_name='Sheet1', index=False)

    writer.close()  
    output.seek(0)

    response = HttpResponse(
            output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=exported_data.xlsx'
    return response


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
        'HS_Code_id__Product_Information',
        'Calender',
    ).annotate(
        total_amount=Sum('Amount')
    )

# ********************Find total amount of each year*******************
    total_amount_year = data.values(
        'Calender'
    ).annotate(
        total_amount = Sum('Amount')
    )

    total_amount_year = total_amount_year.order_by('-Calender')
# *******************************************************************
    
    years = set()
    result_country = {}
    result_hs_code = {}

    for item in total_amount_by_origin_destination:
        year = item['Calender']
        years.add(year)

    for item in total_amount_by_origin_destination:
        origin_destination = item['Origin_Destination__Country_Name']
        hs_code = item['HS_Code_id__HS_Code']
        product_information = item['HS_Code_id__Product_Information']
        year = item['Calender']
        total_amount = item['total_amount']
        
        if origin_destination not in result_country:
            result_country[origin_destination] = {}
        
        if hs_code not in result_hs_code:
            result_hs_code[hs_code] = {'Product_Information': product_information}
         
        for y in years:
            result_country[origin_destination][y] = 0
            result_hs_code[hs_code][y] = 0
    
    for item in total_amount_by_origin_destination:
        origin_destination = item['Origin_Destination__Country_Name']
        hs_code = item['HS_Code_id__HS_Code']
        product_information = item['HS_Code_id__Product_Information']
        year = item['Calender']
        total_amount = item['total_amount']
        result_country[origin_destination][year] = total_amount
        result_hs_code[hs_code][year] =total_amount

    sorted_years = sorted(list(years), reverse=True)
    
    for origin_destination, year_data in result_country.items():
        result_country[origin_destination] = dict(
            sorted(year_data.items(), key=lambda x: x[0], reverse=True))
       
    for hs_code, year_data in result_hs_code.items():
        years = {(key, value) for key, value in year_data.items() if isinstance(key, int)}
        sorted_years = dict(sorted(years, key=lambda x: x[0], reverse=True))
        sorted_years['Product_Information'] = year_data['Product_Information']
        result_hs_code[hs_code] = sorted_years

    context = {'data':data, 'country_categories':country_categories, 'unit_categories':unit_categories,'hs_codes':hs_codes, 'trade_type_categories':trade_type_categories, 'result_country': result_country,'result_hs_code': result_hs_code,
               'years':sorted_years, 'display_country':display_country, 'display_hs_code':display_hs_code, 'queryset_length':len(total_amount_by_origin_destination), 'total_amount_year':total_amount_year, 'tables':tables, 'meta_tables':meta_tables}

    return render(request, 'trade_data/time_series.html', context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
@require_POST
def delete_selected_trade(request):
    selected_ids = request.POST.getlist('selected_items')
    if not selected_ids:
        messages.error(request, 'No items selected for deletion.')
        return redirect('display_trade_table')
    try:
        TradeData.objects.filter(id__in=selected_ids).delete()
        messages.success(request, 'Selected items deleted successfully.')
    except Exception as e:
        messages.error(request, f'Error deleting items: {e}')

    return redirect('display_trade_table')

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def delete_trade_record(request, item_id):
    try:
        item_to_delete = get_object_or_404(TradeData, id=item_id)
        item_to_delete.delete()
        messages.success(request, 'Deleted successfully')
        return redirect('display_trade_table')
    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}")
    
@login_required(login_url = 'login')
def display_country_meta(request):
    data = Country_meta.objects.all().order_by('Country_Name')
    total_data = data.count()

    column_names = Country_meta._meta.fields

    paginator = Paginator(data, 12)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)


    context = {'page': page, 'total_data':total_data, 'meta_tables':meta_tables, 'tables':tables, 'column_names':column_names}
    return render(request, 'trade_data/display_country_meta.html', context)

@login_required(login_url = 'login')
def display_hs_code_meta(request):
    data = HS_Code_meta.objects.all().order_by('HS_Code')
    total_data = data.count()

    column_names = HS_Code_meta._meta.fields

    paginator = Paginator(data, 12)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {'page': page, 'total_data':total_data, 'meta_tables':meta_tables, 'tables':tables, 'column_names':column_names}
    return render(request, 'trade_data/display_hs_code_meta.html', context)

@login_required(login_url = 'login')
def display_unit_meta(request):
    data = Unit_meta.objects.all().order_by('Unit_Name')
    total_data = data.count()

    column_names = Unit_meta._meta.fields

    paginator = Paginator(data, 12)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {'page': page, 'total_data':total_data, 'meta_tables':meta_tables, 'tables':tables, 'column_names':column_names}
    return render(request, 'trade_data/display_unit_meta.html', context)


# Convert duplicate_data to a DataFrame, then to excel
def duplicate_data_to_excel(duplicate_data):
    column_names = list(duplicate_data[0]['data'].keys())
    duplicate_df = pd.DataFrame([d['data'] for d in duplicate_data], columns=column_names)

    # Create a response object with Excel content
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=duplicate_data.xlsx'

    duplicate_df.to_excel(response, index=False, sheet_name='duplicate_data')

    return response

# Get the data from session storage
def download_duplicate_excel(request):
    duplicate_data = request.session.get('duplicate_data', [])

    if duplicate_data:
        response = duplicate_data_to_excel(duplicate_data)
        request.session.pop('duplicate_data', None)
        return response
    else:
        return HttpResponse('No data to export.')
    
def error_data_to_excel(error_data):
    if not error_data:
        # Handle the case where error_data is empty
        return HttpResponse("No data to export.")

    # Extract column names from the first item in error_data
    first_item = error_data[0]
    
    # Check if the first item has the expected structure
    if isinstance(first_item, dict) and 'data' in first_item:
        column_names = list(first_item['data'].keys())
    else:
        return HttpResponse("Invalid data structure.")

    # Extract data from each dictionary in error_data
    data_list = [d['data'] for d in error_data if isinstance(d, dict) and 'data' in d]

    # Create a DataFrame using the extracted data and column names
    error_df = pd.DataFrame(data_list, columns=column_names)

    # Create a response object with Excel content
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=error_data.xlsx'

    # Write the DataFrame to the Excel response
    error_df.to_excel(response, index=False, sheet_name='error_data')

    return response

def download_error_excel(request):
    error_data = request.session.get('errors', [])

    if error_data:
        response = error_data_to_excel(error_data)
        request.session.pop('error_data', None)
        return response
    else:
        return HttpResponse('No data to export.')