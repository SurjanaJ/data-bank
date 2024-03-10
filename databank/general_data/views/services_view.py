from django.db import IntegrityError
from django.shortcuts import redirect, render
import pandas as pd
from numpy import NaN
from django.db.models import Q
from django.forms import model_to_dict
from datetime import date
from django.contrib import messages

from ..forms import UploadServicesForm

from trade_data.models import Country_meta
from ..models import Services, Services_Meta
from trade_data import views
from trade_data.views import is_valid_queryparam, tables
from django.core.paginator import Paginator, Page

from django.contrib.auth.decorators import login_required
from accounts.decorators import allowed_users

@login_required(login_url = 'login')
def display_services_meta(request):
    data = Services_Meta.objects.all()
    total_data = data.count()

    column_names = Services_Meta._meta.fields

    context = {'data': data, 'total_data':total_data, 'meta_tables':views.meta_tables, 'tables':tables, 'column_names':column_names}
    
    return render(request, 'general_data/display_meta.html', context)

@login_required(login_url = 'login')
def display_services_table(request):
    data = Services.objects.all()
    column_names = Services._meta.fields
    new_field = 'Services_Type'
    new_column = tuple(column_names) + (new_field,)

    country_categories = Country_meta.objects.all()
    direction_categories = [choice[1] for choice in Services.DIRECTION_OPTIONS]
    service_code = Services_Meta.objects.all()

    year_min = request.GET.get('year_min')
    year_max = request.GET.get('year_max')
    value_min = request.GET.get('value_min')
    value_max = request.GET.get('value_max')
    direction = request.GET.get('direction')
    origin_destination  = request.GET.get('origin_destination')
    country = request.GET.get('country')
    code = request.GET.get('code')

    if is_valid_queryparam(year_min):
        data = data.filter(Year__gte=year_min)

    if is_valid_queryparam(year_max):
        data = data.filter(Year__lt = year_max)

    if is_valid_queryparam(country) and country != '--':
        data = data.filter(Country_id=country)

    if is_valid_queryparam(value_min):
        data = data.filter(Value__gte=value_min)

    if is_valid_queryparam(value_max):
        data = data.filter(Value__lt=value_max)

    if is_valid_queryparam(direction) and direction != '--':
        data = data.filter(Direction=direction) 

    if is_valid_queryparam(code) and code != '--':
        data = data.filter(Code=code)

    if is_valid_queryparam(origin_destination) and origin_destination != '--':
        data = data.filter(Origin_Destination_id=origin_destination)
    
    
    paginator = Paginator(data, 40)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = { 'data_len': len(data), 'country_categories': country_categories, 'direction_categories': direction_categories, 'service_code':service_code ,'page':page, 'query_len': len(page), 'tables':tables, 'meta_tables':views.meta_tables, 'column_names':new_column}

    return render(request, 'general_data/services_templates/services_table.html', context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def upload_services_excel(request):
    errors = []
    duplicate_data = []
    updated_count = 0
    added_count = 0

    if request.method == 'POST':
        form = UploadServicesForm(request.POST,request.FILES)
        if form.is_valid():
            excel_data = request.FILES['file']
            df = pd.read_excel(excel_data)
            df.fillna('', inplace=True)
            df['Year'] = pd.to_datetime(df['Year']).dt.date

            for index, row in df.iterrows():
                try: 
                    Year = row['Year']
                    Country = Country_meta.objects.get(Country_Name = row['Country'])
                    Origin_Destination = Country_meta.objects.get(
                        Country_Name=row['Origin_Destination'])
                    Code = Services_Meta.objects.get(Code = row['Code'])
                    direction = row['Direction']

                    if direction not in ['Import', 'Export']:
                        raise ValueError(
                            f"Invalid Direction at row {index} : {direction}"
                        )
                    services_data = {
                        'Country':Country,
                        'Year':Year,
                        'Direction':row['Direction'],
                        'Code':Code,
                        'Value':row['Value'],
                        'Origin_Destination': Origin_Destination
                    }

                except Exception as e:
                    services_data['Year']=Year.isoformat()
                    errors.append({'row_index': index, 'data': services_data, 'reason': str(e)})
                    
                    continue

                existing_record = Services.objects.filter(
                        Q(Country=Country) & 
                        Q(Year=Year) & 
                        Q(Direction = services_data['Direction']) &  
                        Q(Code=Code) & 
                        Q(Origin_Destination=Origin_Destination)   
                        ).first()
                
                if existing_record:
                    existing_dict = model_to_dict(existing_record)
                    services_data_dict = model_to_dict(Services(**services_data))

                    if all(existing_dict[key] == services_data_dict[key] or (pd.isna(existing_dict[key]) and pd.isna(services_data_dict[key])) for key in services_data_dict if key !='id'):
                        services_data = {
                            'Country':Country.Country_Name,
                        'Year':Year.isoformat(),
                        'Direction':row['Direction'],
                        'Code':Code.Code,
                        'Services_Type': row['Services_Type'],
                        'Value':row['Value'],
                        'Origin_Destination': Origin_Destination.Country_Name,
                        }

                        duplicate_data.append({
                            'row_index': index,
                            'data': {key: str(services_data[key])if isinstance(services_data[key], date) else services_data[key] for key in services_data}
                        })

                    
                    else:
                        for key, value in services_data.items():
                            setattr(existing_record, key, value)
                            

                        try:
                            existing_record.save()
                            updated_count += 1
                            
                        except IntegrityError as e:
                            errors.append(f"Error updating row {index}: {e}")
                            

                else:
                    try:
                        servicesData = Services(**services_data)
                        servicesData.save()
                        added_count +=1
                        
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
                return redirect('services_table')  
            
    else:
        form = UploadServicesForm()

    return render(request,'general_data/transport_templates/upload_transport_form.html',{'form':form})
