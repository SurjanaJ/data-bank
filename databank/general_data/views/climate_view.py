from datetime import date
from django.db import IntegrityError
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
            cols = df.columns.tolist()
            df.fillna('', inplace=True)
            df['Date'] = pd.to_datetime(df['Date']).dt.date

            for index, row in df.iterrows():
                climate_data = {col: row[col] for col in cols}
                try:
                    Date = row['Date']
                    Country = Country_meta.objects.get(Country_Name = row['Country'])
                    Place = Climate_Place_Meta.objects.get(Place_Name = row['Place'])
                    Temperature_Unit = Unit_meta.objects.get(Unit_Code=row['Temperature_Unit'])
                    Climate_Unit = Unit_meta.objects.get(Unit_Code=row['Climate_Unit'])

                    climate_type = row['Climate']
                    if climate_type not in ['Rain', 'Snow','Storm']:
                        raise ValueError(f"Invalid Climate at row {index}: {climate_type}")
                    
                    climate_data = {
                        'Country': Country,
                        'Date': row['Date'],
                        'Place':Place,
                        'Temperature_Unit': Temperature_Unit,
                        'Max_Temperature': row['Max_Temperature'],
                        'Min_Temperature': row['Min_Temperature'],
                        'Climate': row['Climate'],
                        'Climate_Unit' : Climate_Unit,
                        'Amount': row['Amount'],
                    }
                
                except Exception as e:
                    climate_data['Date'] = Date.isoformat()
                    errors.append({'row_index': index, 'data': climate_data, 'reason': str(e)})      
                    continue     

                existing_record = Climate_Data.objects.filter(
                    Q(Country = Country)
                    & Q(Date = Date)
                    & Q(Place = Place)
                ).first()

                if existing_record:
                    existing_dict = model_to_dict(existing_record)
                    climate_data_dict = model_to_dict(Climate_Data(**climate_data))

                    if all(existing_dict[key] == climate_data_dict[key] or (pd.isna(existing_dict[key]) and pd.isna(climate_data_dict[key])) for key in climate_data_dict if key != 'id'):
                        climate_data = {
                            'Country': Country.Country_Name,
                            'Date': Date.isoformat(),
                            'Place':Place.Place_Name,
                            'Temperature_Unit': Temperature_Unit.Unit_Code,
                            'Max_Temperature': row['Max_Temperature'],
                            'Min_Temperature': row['Min_Temperature'],
                            'Climate': row['Climate'],
                            'Climate_Unit' : Climate_Unit.Unit_Code,
                            'Amount': row['Amount'],
                        }

                        duplicate_data.append({
                            
                            'row_index': index,
                            'data': {key: str(climate_data[key]) if isinstance(climate_data[key], date) else climate_data[key] for key in climate_data}
                        })
                       
                    else:
                        for key, value in climate_data.items():
                            setattr(existing_record, key, value)
                            try:
                                existing_record.save()
                                updated_count += 1
                            
                            except IntegrityError as e:
                                errors.append(f"Error updating row {index}: {e}")
                            
                else:
                    try:
                        climateData = Climate_Data(**climate_data)
                        climateData.save()
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