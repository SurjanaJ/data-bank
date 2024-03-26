from datetime import datetime
from django.db import DataError
from django.forms import model_to_dict
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Q
import pandas as pd

from .energy_view import strip_spaces
from ..models import Health_disease, Country_meta,Health_disease_Meta
from ..forms import UploadHealthDiseaseForm
from trade_data.views import tables
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import F
from io import BytesIO
from django.http import HttpResponse
from trade_data import views

from django.contrib.auth.decorators import login_required
from accounts.decorators import allowed_users


def is_valid_queryparam(param):
    return param !='' and param is not None

@login_required(login_url = 'login')
def display_health_disease_table(request):
    data=Health_disease.objects.all()
    country_categories=Country_meta.objects.all()
    health_disease_codes=Health_disease_Meta.objects.all()

    unit_categories=[choice[1] for choice in Health_disease.Unit_Options]


    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    country_category = request.GET.get('country_category')
    unit=request.GET.get('unit')
    disease_code = request.GET.get('health_disease_code')
    minimum_number = request.GET.get('minimum_number')
    maximum_number = request.GET.get('maximum_number')

    if is_valid_queryparam(date_min):
        data=data.filter(Year__gte=date_min)

    if is_valid_queryparam(date_max):
        data=data.filter(Year__lt=date_max)

    if is_valid_queryparam(country_category) and country_category != '--':
        data = data.filter(Country_id=country_category)

    if is_valid_queryparam(disease_code) and disease_code != '--':
        data=data.filter(Disease_Code = disease_code)

    if is_valid_queryparam(unit)  and unit != '--':
        data=data.filter(Unit=unit)

    if is_valid_queryparam(minimum_number):
        data=data.filter(Number_Of_Case__gte=minimum_number)

    if is_valid_queryparam(maximum_number):
        data=data.filter(Number_Of_Case__lt=maximum_number)


    #get form data for filteration
    
    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context={
        'data_len':len(data),
        'query_len': len(page),
        'page':page,    
        'country_categories':country_categories,
        'unit_categories':unit_categories,
        'health_disease_codes':health_disease_codes,
        'tables':tables
    }

    return render(request, 'general_data/health_disease_templates/health_disease_table.html',context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def upload_health_diseases_excel(request):
    errors = []
    duplicate_data = []
    updated_count = 0
    added_count = 0

    if request.method == 'POST':
        form = UploadHealthDiseaseForm(request.POST,request.FILES)
        if form.is_valid():
            excel_data = request.FILES['file']
            df = pd.read_excel(excel_data,dtype={'Disease Code':str})
            df.fillna('',inplace=True)
            df = df.map(strip_spaces)

             # Check if required columns exist
            required_columns = ['Year', 'Country', 'Disease Code','Unit','Number Of Case']  # Add your required column names here
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                errors.append(f"Missing columns: {', '.join(missing_columns)}")
                return render(request,'general_data/invalid_upload.html', {'missing_columns': missing_columns, 'tables': tables, 'meta_tables': views.meta_tables,} )
            

            if 'id' in df.columns:
                for index, row in df.iterrows():
                    id = row.get('id') 
                    data = {
                        'Year':row['Year'],
                        'Country': row['Country'],
                        'Disease Code': row['Disease Code'],
                        'Unit': row['Unit'],
                        'Number Of Case':row['Number Of Case']
                    }

                    try:
                        health_disease_instance = Health_disease.objects.get(id=id)
                        health_data = data

                        try:
                            country = Country_meta.objects.get(Country_Name=row['Country'])
                            code = Health_disease_Meta.objects.get(Code = row['Disease Code'])
                      

                            health_disease_instance.Year = row['Year']
                            health_disease_instance.Country = country
                            health_disease_instance.Disease_Code = code
                            health_disease_instance.Unit = row['Unit']
                            health_disease_instance.Number_Of_Case = row['Number Of Case']
                            
                            
                            health_disease_instance.save()
                            updated_count +=1
                        except Exception as e:
                            health_data= data
                            errors.append({'row_index': index, 'data': health_data, 'reason': str(e)})
                            continue
                    except Exception as e:
                            health_data= data
                            errors.append({
                                            'row_index': index,
                                            'data': health_data,
                                            'reason': f'Error inserting row {index}: {e}'
                                        })
                            continue
                    
            else:    
                for index,row in df.iterrows():
                    data = {
                        'Year':row['Year'],
                        'Country': row['Country'],
                        'Disease Code': row['Disease Code'],
                        'Unit': row['Unit'],
                        'Number Of Case':row['Number Of Case']
                    }
                    try:

                        country = Country_meta.objects.get(Country_Name = row['Country'])
                        code = Health_disease_Meta.objects.get (Code=row['Disease Code'])

                        existing_record = Health_disease.objects.filter(
                            Q(Year = row['Year'])
                            & Q(Country = country)
                            & Q(Disease_Code = code)
                            & Q(Unit= row['Unit'])
                            & Q(Number_Of_Case = row['Number Of Case'])
                        ).first()
                    
                        if existing_record:
                            health_data = data
                            duplicate_data.append({
                                'row_index': index,
                                'data': {key: str(value) for key, value in health_data.items()}
                            })
                            continue
                        else:
                            try:
                                health_data = {
                                    'Year':row['Year'],
                                    'Country': country,
                                    'Disease_Code': code,
                                    'Unit': row['Unit'],
                                    'Number_Of_Case':row['Number Of Case']
                                }
                                healthData = Health_disease(**health_data)
                                healthData.save()
                                added_count += 1
                            except Exception as e:
                                errors.append(f"Error inserting row {index}: {e}")
                    
                    except Exception as e:
                        health_data = data
                        errors.append({'row_index': index, 'data': health_data, 'reason': str(e)})
                        continue
                    
            if added_count > 0:
                messages.success(request, str(added_count) + ' records added.')

            if updated_count >0:
                messages.info(request, str(updated_count) + ' records updated.')

            if errors:
                request.session['errors'] = errors
                return render(request, 'trade_data/error_template.html', {'errors': errors})
            elif duplicate_data:
                request.session['duplicate_data'] = duplicate_data
                return render(request,'trade_data/duplicate_template.html', {'duplicate_data': duplicate_data})
            else:
                return redirect('health_disease_table')
    else:
        form = UploadHealthDiseaseForm()
    return render(request,'general_data/transport_templates/upload_transport_form.html',{'form':form})


@login_required(login_url = 'login')
def display_health_disease_meta(request):
    data = Health_disease_Meta.objects.all()
    total_data = data.count()

    column_names = Health_disease_Meta._meta.fields

    context = {'data': data, 'total_data':total_data, 'meta_tables':views.meta_tables, 'tables':tables, 'column_names':column_names}
    return render(request, 'general_data/display_meta.html', context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def update_selected_health_disease(request):
    selected_ids = request.POST.getlist('selected_items')
    if not selected_ids:
        messages.error(request, 'No items selected.')
        return redirect('health_disease_table')

    else:
        queryset = Health_disease.objects.filter(id__in=selected_ids)
        queryset = queryset.annotate(
        country = F('Country__Country_Name'),
        disease_code = F('Disease_Code__Code'),
        disease_type = F('Disease_Code__Disease_Type'),
        )

        df = pd.DataFrame(list(queryset.values('id','Year','country','disease_code','disease_type','Unit','Number_Of_Case')))
        df.rename(columns={'country': 'Country', 'disease_code':'Disease Code','disease_type':'Disease Type','Number_Of_Case':'Number Of Case'}, inplace=True)
        df = df[['id','Year','Country','Disease Code','Disease Type','Unit','Number Of Case']]
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')  
        df.to_excel(writer, sheet_name='Sheet1', index=False)
        writer.close()  
        output.seek(0)

        response = HttpResponse(
            output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=exported_data.xlsx'
        return response