from datetime import date
from django.db import IntegrityError

from .energy_view import strip_spaces
from ..forms import UploadClimateForm, UploadClimatePlaceMeta
from ..models import Climate_Data, Climate_Place_Meta
from trade_data.models import Country_meta, Unit_meta

from trade_data import views
from io import BytesIO
from django.forms import model_to_dict
from django.shortcuts import redirect, render
import pandas as pd
from django.contrib import messages
from django.core.paginator import Paginator
from trade_data.views import is_valid_queryparam, tables
from django.http import HttpResponse
from django.db.models import F, Q

def upload_climate_place_meta_excel(request):
    errors = []
    duplicate_data = []
    added_count = 0
    updated_count = 0

    if request.method == 'POST':
        form = UploadClimatePlaceMeta(request.POST, request.FILES)

        if form.is_valid():
            excel_data = request.FILES['meta_file']
            df = pd.read_excel(excel_data, dtype={'Place_Code':str})
            df.fillna('', inplace= True)


            for index, row in df.iterrows():
                place_data = {
                    'Country': row['Country'],
                    'Place_Code': row['Place_Code'],
                    'Place_Name': row['Place_Name']
                }
                
                try:
                    Country = Country_meta.objects.get(Country_Name = row['Country'])

                    place_data = {
                        'Country': Country,
                        'Place_Code': row['Place_Code'],
                        'Place_Name': row['Place_Name']
                    }
                    
                except Exception as e:
                    errors.append({'row_index': index, 'data': place_data, 'reason': str(e)})
                    continue

                existing_record = Climate_Place_Meta.objects.filter(
                        Q(Country=Country) & Q(Place_Code=row['Place_Code']) 
                        ).first()
                
                if existing_record:
                    existing_dict = model_to_dict(existing_record)
                    place_data_dict = model_to_dict(Climate_Place_Meta(**place_data))

                    if all(existing_dict[key] == place_data_dict[key] or (pd.isna(existing_dict[key]) and pd.isna(place_data_dict[key])) for key in place_data_dict if key != 'id'):
                        place_data = {
                            'Country': Country.Country_Name,
                            'Place_Code': row['Place_Code'],
                            'Place_Name': row['Place_Name']
                        }

                        duplicate_data.append({
                             'row_index': index,
                                'data': {key: str(value) for key, value in place_data.items()}
                        })

                    else:
                        for key, value in place_data.items():
                                setattr(existing_record, key, value)
                        try:
                            existing_record.save()
                            updated_count += 1
                        except IntegrityError as e:
                                errors.append(f"Error updating row {index}: {e}")
                
                else:
                    try:
                        placeData = Climate_Place_Meta(**place_data)
                        placeData.save()
                        added_count += 1
                    except Exception as e:
                        errors.append(f"Error inserting row {index}: {e}")

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
                return redirect('place_meta')
    else:
        form = UploadClimatePlaceMeta()

    return render(request,'general_data/transport_templates/upload_transport_form.html',{'form':form})

def display_climate_place_meta(request):
    data = Climate_Place_Meta.objects.all()
    total_data = data.count()
    
    column_names = Climate_Place_Meta._meta.fields

    context = {'data':data, 'total_data':total_data, 'meta_tables':views.meta_tables, 'tables':tables, 'column_names':column_names}

    return render(request, 'general_data/display_meta.html', context)


def upload_climate_excel(request):
    errors = []
    duplicate_data = []
    updated_count = 0
    added_count = 0

    if request.method == 'POST':
        form = UploadClimateForm(request.POST, request.FILES)
        if form.is_valid():
            excel_data = request.FILES['file']
            df = pd.read_excel(excel_data)
            df.fillna('', inplace=True)
            df['Date'] = pd.to_datetime(df['Date']).dt.date
            df = df.map(strip_spaces)

            # Update the existing data
            if 'id' in df.columns:
                for index, row in df.iterrows():
                    id = row.get('id')
                    data ={
                        'Country': row['Country'],
                        'Date': row['Date'].isoformat(),
                        'Place':row['Place'],
                        'Temperature_Unit': row['Temperature Unit'],
                        'Max_Temperature': row['Max Temperature'],
                        'Min_Temperature': row['Min Temperature'],
                        'Climate': row['Climate'],
                        'Climate_Unit' : row['Climate Unit'],
                        'Amount': row['Amount'],
                    }
                    try:
                        climate_instance = Climate_Data.objects.get(id = id)
                        climate_data = data

                        try:
                            Date = row['Date']
                            Country = Country_meta.objects.get(Country_Name = row['Country'])
                            Place = Climate_Place_Meta.objects.get(Place_Code = row['Place'])
                            Temperature_Unit = Unit_meta.objects.get(Unit_Code=row['Temperature Unit'])
                            Climate_Unit = Unit_meta.objects.get(Unit_Code=row['Climate Unit'])

                            climate_type = row['Climate']
                            if climate_type not in ['Rain', 'Snow','Storm']:
                                raise ValueError(f"Invalid Climate at row {index}: {climate_type}")

                            climate_instance.Country = Country
                            climate_instance.Date= Date
                            climate_instance.Place = Place
                            climate_instance.Temperature_Unit = Temperature_Unit
                            climate_instance.Max_Temperature = row['Max Temperature']
                            climate_instance.Min_Temperature = row['Min Temperature']
                            climate_instance.Climate = climate_type
                            climate_instance.Climate_Unit = Climate_Unit
                            climate_instance.Amount = row['Amount']

                            climate_instance.save()
                            updated_count += 1
                            
                        # meta data not present
                        except Exception as e:
                            climate_data = data
                            errors.append({'row_index': index, 'data': climate_data, 'reason': str(e)})
                            continue
                    
                    except Exception as e:
                        climate_data = data
                        errors.append({
                                    'row_index': index,
                                    'data': climate_data,
                                    'reason': f'Error inserting row {index}: {e}'
                                })
                        continue
            
            # Add new records
            else:
                for index, row in df.iterrows():
                    data ={
                        'Country': row['Country'],
                        'Date': row['Date'].isoformat(),
                        'Place':row['Place'],
                        'Temperature_Unit': row['Temperature Unit'],
                        'Max_Temperature': row['Max Temperature'],
                        'Min_Temperature': row['Min Temperature'],
                        'Climate': row['Climate'],
                        'Climate_Unit' : row['Climate Unit'],
                        'Amount': row['Amount'],
                    }
                    try:
                        Date = row['Date']
                        Country = Country_meta.objects.get(Country_Name = row['Country'])
                        Place = Climate_Place_Meta.objects.get(Place_Code = row['Place'])
                        Temperature_Unit = Unit_meta.objects.get(Unit_Code=row['Temperature Unit'])
                        Climate_Unit = Unit_meta.objects.get(Unit_Code=row['Climate Unit'])

                        climate_type = row['Climate']
                        if climate_type not in ['Rain', 'Snow','Storm']:
                            raise ValueError(f"Invalid Climate at row {index}: {climate_type}")

                        climate_data = {
                            'Country': Country,
                            'Date':Date.isoformat(),
                            'Place': Place,
                            'Temperature_Unit' : Temperature_Unit,
                            'Max_Temperature': row['Max Temperature'],
                            'Min_Temperature': row['Min Temperature'],
                            'Climate': climate_type,
                            'Climate_Unit':Climate_Unit,
                            'Amount': row['Amount']
                        }

                        existing_record = Climate_Data.objects.filter(
                            Q(Country = Country)
                            & Q(Date = Date)
                            & Q(Place = Place)
                            & Q(Temperature_Unit=Temperature_Unit)
                            & Q(Max_Temperature = row['Max Temperature'])
                            & Q(Min_Temperature = row['Min Temperature'])
                            & Q(Climate = climate_type)
                            & Q(Climate_Unit= Climate_Unit)
                            & Q(Amount = row['Amount'])
                        ).first()

                        if existing_record:
                            climate_data= data

                            duplicate_data.append({
                                'row_index': index,
                                'data': {key: str(value) for key, value in climate_data.items()}
                            })
                            continue

                        else:
                            try:
                                ClimateData = Climate_Data(**climate_data)
                                ClimateData.save()
                                added_count += 1
                            except Exception as e:
                                errors.append(f"Error inserting row {index}: {e}")
                            
                    except Exception as e:
                        climate_data = data
                        errors.append({'row_index': index, 'data': climate_data, 'reason': str(e)})
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
            return redirect('climate_table') 

    else:
        form = UploadClimateForm()
    
    return render(request,'general_data/transport_templates/upload_transport_form.html',{'form':form})

def display_climate_table(request):
    data = Climate_Data.objects.all()

    country_categories = Country_meta.objects.all()
    unit_categories = Unit_meta.objects.all()
    place_categories = Climate_Place_Meta.objects.all()
    climate_type_categories = [choice[1] for choice in Climate_Data.CLIMATE_OPTIONS]

    date_minimum = request.GET.get('date_minimum')
    date_maximum = request.GET.get('date_maximum')
    country = request.GET.get('country')
    place = request.GET.get('place')
    temperature_unit = request.GET.get('temperature_unit')
    climate_type = request.GET.get('climate_type')
    climate_unit = request.GET.get('climate_unit')

    if is_valid_queryparam(date_minimum):
        data = data.filter(Date__gte = date_minimum)

    if is_valid_queryparam(date_maximum):
        data = data.filter(Date__lt = date_maximum)

    if is_valid_queryparam(country) and country != '--':
        data = data.filter(Country_id=country)
    
    if is_valid_queryparam(place) and place != '--':
        data = data.filter(Place_id=place)

    if is_valid_queryparam(temperature_unit) and temperature_unit !='--':
        data = data.filter(Temperature_Unit_id = temperature_unit)

    if is_valid_queryparam(climate_type) and climate_type != '--':
        data = data.filter(Climate=climate_type) 

    if is_valid_queryparam(climate_unit) and climate_unit !='--':
        data = data.filter(Climate_Unit_id = climate_unit)

    paginator = Paginator(data, 40)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context ={'data_len':len(data),
              'page':page, 
              'query_len':len(page), 
              'tables': tables, 
              'meta_tables': views.meta_tables,'country_categories':country_categories,
              'unit_categories':unit_categories,
              'place_categories':place_categories,
              'climate_type_categories':climate_type_categories
                      }
    return render(request, 'general_data/climate_templates/climate_table.html', context)


def export_climate_excel(request):
    date_minimum = request.GET.get('date_minimum')
    date_maximum = request.GET.get('date_maximum')
    country = request.GET.get('country')
    place = request.GET.get('place')
    temperature_unit = request.GET.get('temperature_unit')
    climate_type = request.GET.get('climate_type')
    climate_unit = request.GET.get('climate_unit')

    filter_conditions = {}
    if is_valid_queryparam(date_minimum):
        filter_conditions['Date__gte'] = date_minimum

    if is_valid_queryparam(date_maximum):
        filter_conditions['Date__lt'] = date_maximum

    if is_valid_queryparam(country) and country != '--':
        filter_conditions['Country'] = country
    
    if is_valid_queryparam(place) and place != '--':
        filter_conditions['Place'] = place

    if is_valid_queryparam(temperature_unit) and temperature_unit !='--':
        filter_conditions['Temperature_Unit'] = temperature_unit

    if is_valid_queryparam(climate_type) and climate_type != '--':
        filter_conditions['Climate'] = climate_type

    if is_valid_queryparam(climate_unit) and climate_unit !='--':
        filter_conditions['Climate_Unit'] = climate_unit

    queryset = Climate_Data.objects.filter(**filter_conditions)
    queryset = queryset.annotate(
        country = F('Country__Country_Name'),
        place = F('Place__Place_Name'),
        temperature_unit = F('Temperature_Unit__Unit_Name'),
        climate_unit = F('Climate_Unit__Unit_Name')
    )

    data = pd.DataFrame(list(queryset.values('country','Date', 'place','temperature_unit','Max_Temperature', 'Min_Temperature', 'Climate', 'climate_unit','Amount')))

    data.rename(columns={'country':'Country','place': 'Place', 'temperature_unit':'Temperature_Unit', 'climate_unit':'Climate_Unit'}, inplace=True)

    column_order = ['Country', 'Date', 'Place', 'Temperature_Unit', 'Max_Temperature', 'Min_Temperature','Climate','Climate_Unit','Amount']

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


def update_selected_climate(request):
    selected_ids = request.POST.getlist('selected_items')
    if not selected_ids:
        messages.error(request, 'No items selected.')
        return redirect('climate_table')
    else:
        queryset = Climate_Data.objects.filter(id__in=selected_ids)
        queryset = queryset.annotate(
        country = F('Country__Country_Name'),
        place = F('Place__Place_Code'),
        place_name = F('Place__Place_Name'),
        temperature_unit = F('Temperature_Unit__Unit_Code'),
        climate_unit = F('Climate_Unit__Unit_Code')
    )
        data = pd.DataFrame(list(queryset.values('id','Date','country','place', 'place_name','temperature_unit','Max_Temperature','Min_Temperature','Climate','climate_unit','Amount')))
        
        data.rename(columns={
                         'country':'Country',
                         'place':'Place',
                         'place_name':'Place Name',
                         'temperature_unit': 'Temperature Unit',
                         'climate_unit': 'Climate Unit',
                         'Max_Temperature':'Max Temperature',
                         'Min_Temperature':'Min Temperature'
                         }, inplace=True)
        
        column_order = ['id','Country','Date','Place','Place Name', 'Temperature Unit','Max Temperature','Min Temperature','Climate','Climate Unit','Amount']

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
