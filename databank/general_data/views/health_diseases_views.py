from datetime import datetime
from django.db import DataError
from django.forms import model_to_dict
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Q
import pandas as pd
from ..models import Health_disease, Country_meta,Health_disease_Meta
from ..forms import UploadHealthDiseaseForm
from trade_data.views import tables
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.views.decorators.http import require_POST


def is_valid_queryparam(param):
    return param !='' and param is not None


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

def upload_health_diseases_excel(request):
    errors = []
    duplicate_data = []
    updated_count = 0
    added_count = 0

    if request.method == 'POST':
        form = UploadHealthDiseaseForm(request.POST,request.FILES)
        if form.is_valid():
            excel_data = request.FILES['file']
            df = pd.read_excel(excel_data,dtype={'Disease_Code':str})
            cols = df.columns.to_list()
            df.fillna('',inplace=True)


            for index,row in df.iterrows():
                health_disease_data = {col: row[col] for col in cols}
                try:
                    unit_options = [option[0] for option in Health_disease.Unit_Options]

                    Country = Country_meta.objects.get(Country_Name = row['Country'])
                    disease_code = Health_disease_Meta.objects.get (Code=row['Disease_Code'])
                    unit = row['Unit']

                    if unit not in unit_options:
                        raise ValueError(f"Invalid Unit at row {index}: {unit}")

                    health_disease_data = {
                        'Year':row['Year'],
                        'Country':Country,
                        'Disease_Code':disease_code,
                        'Unit':unit,    
                        'Number_Of_Case':row['Number_Of_Case']                    
                    }
                except Exception as e:
                    errors.append({'row_index': index, 'data': health_disease_data, 'reason': str(e)})
                    continue

                existing_record = Health_disease.objects.filter(
                    Q(Country=Country) & Q(Year = row['Year']) & Q(Unit = health_disease_data['Unit']) & Q(Disease_Code = disease_code)
                ).first()
                
                if existing_record:
                    existing_dict = model_to_dict(existing_record)
                    health_disease_data_dict = model_to_dict(Health_disease(**health_disease_data))
                    if all(existing_dict[key] == health_disease_data_dict[key] or (pd.isna(existing_dict[key])and pd.isna(health_disease_data_dict[key])) for key in health_disease_data_dict if key != 'id' ):
                        health_disease_data = {
                            'Year':row['Year'],
                            'Country':Country,
                            'Disease_Code':disease_code,
                            'Unit':unit,    
                            'Number_Of_Case':row['Number_Of_Case']

                        }
                        duplicate_data.append({
                            'row_index':index,
                            'data':{key:str(value)for key,value in health_disease_data.items()}
                        })
                    else:
                        for key ,value in health_disease_data.items():
                            setattr(existing_record,key ,  value)
                        try:
                            existing_record.save()
                            updated_count +=1

                        except IntegrityError  as e:
                            errors.append({'row_index': index, 'data': health_disease_data, 'reason': str(e)})
                else:
                    try:
                        HealthDiseaseData = Health_disease(**health_disease_data)
                        HealthDiseaseData.save()
                        added_count +=1
                    
                    except Exception as e:
                        errors.append({'row_index': index, 'data': health_disease_data, 'reason': str(e)})

            if added_count > 0:
                messages.success(request, str(added_count) + ' records added.')

            if updated_count >0:
                messages.info(request, str(updated_count) + ' records updated.')

            if errors:
                request.session['errors'] = errors
                return render(request, 'trade_data/error_template.html', {'errors': errors})
            elif duplicate_data:
                request.session['duplicate_data'] = duplicate_data
                return render(request, 'trade_data/duplicate_template.html', {'duplicate_data': duplicate_data})
            else:
                return redirect('health_disease_table')
    else:
        form = UploadHealthDiseaseForm()
    return render(request,'general_data/transport_templates/upload_transport_form.html',{'form':form})