from datetime import datetime
from django.db import DataError
from django.forms import model_to_dict
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Q
import pandas as pd
from ..models import Mining, Country_meta,Mine_Meta
from ..forms import UploadMiningForm
from trade_data.views import tables
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.views.decorators.http import require_POST

from trade_data import views

def is_valid_queryparam(param):
    return param !='' and param is not None


def display_mining_table(request):

    data = Mining.objects.all()
    mine_codes=Mine_Meta.objects.all()
    unit_options = [choice[1] for choice in Mining.Unit_Options ]

    country_categories = Country_meta.objects.all()

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    country_category = request.GET.get('country_category')
    mine_code = request.GET.get('mine_code')
    unit = request.GET.get('mine_unit')  
    minimum_current_production = request.GET.get('minimum_current_production')
    maximum_current_production = request.GET.get('maximum_current_production')
    minimum_potential_stock = request.GET.get('minimum_potential_stock')
    maximum_potential_stock = request.GET.get('maximum_potential_stock')
    mining_company_name = request.GET.get('mining_company_name')

  
    if is_valid_queryparam(date_min):
        data=data.filter(Year__gte=date_min)

    if is_valid_queryparam(date_max):
        data=data.filter(Year__lt=date_max)

    if is_valid_queryparam(country_category) and country_category != '--':
        data = data.filter(Country_id=country_category)

    if is_valid_queryparam(mine_code) and mine_code != '--':
        data=data.filter(Name_Of_Mine_id = mine_code)

    if is_valid_queryparam(unit)  and unit != '--':
        data=data.filter(Unit=unit) 

    if is_valid_queryparam(minimum_current_production):
        data = data.filter(Current_Production__gte=minimum_current_production)

    if is_valid_queryparam(maximum_current_production):
        data = data.filter(Current_Production__lt=maximum_current_production)

    if is_valid_queryparam(minimum_potential_stock):
        data = data.filter(Potential_Stock__gte=minimum_potential_stock)

    if is_valid_queryparam(maximum_potential_stock):
        data = data.filter(Potential_Stock__lt=maximum_potential_stock)

    if is_valid_queryparam(mining_company_name):
        data=data.filter(Q(Mining_Company_Name__icontains=mining_company_name)).distinct()


    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    

    context={
        'tables':tables,
        'data_len':len(data),
        'query_len': len(page),
        'page':page,
        'country_categories':country_categories,
        'unit_options':unit_options,
        'mine_codes':mine_codes,

    }
    return render(request, 'general_data/mining_templates/mining_table.html',context)


def upload_mining_excel(request):
    errors = []
    duplicate_data = []
    updated_count = 0
    added_count = 0

    if request.method == 'POST':
        form = UploadMiningForm(request.POST,request.FILES)
        if form.is_valid():
            excel_data = request.FILES['file']
            df = pd.read_excel(excel_data)
            cols = df.columns.to_list()
            df.fillna('',inplace=True)

            for index,row in df.iterrows():
                health_disease_data = {col: row[col] for col in cols}
                try:
                    unit_options = [option[0] for option in Mining.Unit_Options]

                    Country = Country_meta.objects.get(Country_Name = row['Country'])
                    mine_type = Mine_Meta.objects.get (Mine_Type=row['Name_Of_Mine'])
                    unit = row['Unit']

                    if unit not in unit_options:
                        raise ValueError(f"Invalid Unit at row {index}: {unit}")

                    mining_data = {
                        'Year':row['Year'],
                        'Country':Country,
                        'Name_Of_Mine':mine_type,
                        'Unit':unit,
                        'Current_Production':row['Current_Production'],                        
                        'Potential_Stock':row['Potential_stock'],
                        'Mining_Company_Name':row['Mining_Company_Name'],
                    }
                except Exception as e:
                    errors.append({'row_index': index, 'data': mining_data, 'reason': str(e)})
                    continue

                existing_record = Mining.objects.filter(
                    Q(Country=Country) & Q(Year = row['Year']) & Q(Unit = mining_data['Unit']) & Q(Name_Of_Mine = mine_type)
                    
                ).first()

                if existing_record:
                    existing_dict = model_to_dict(existing_record)
                    mining_data_dict = model_to_dict(Mining(**mining_data))
                    if all(existing_dict[key]== mining_data_dict[key] or pd.isna(existing_dict[key]) and pd.isna(mining_data_dict[key]) for key in mining_data_dict if key != 'id'):
                        mining_data ={
                            'Year':row['Year'],
                            'Country':Country,
                            'Name_Of_Mine':mine_type,
                            'Unit':unit,
                            'Current_Production':row['Current_Production'],                        
                            'Potential_Stock':row['Potential_stock'],
                            'Mining_Company_Name':row['Mining_Company_Name'],
                        }
                        duplicate_data.append({
                            'row_index':index,
                            'data':{key:str(value)for key,value in mining_data.items()}
                        })
                    else:
                        for key ,value in mining_data.items():
                            setattr(existing_record,key ,  value)
                        try:
                            existing_record.save()
                            updated_count +=1

                        except IntegrityError  as e:
                            errors.append({'row_index': index, 'data': mining_data, 'reason': str(e)})

                else:
                    try:
                        HealthDiseaseData = Mining(**mining_data)
                        HealthDiseaseData.save()
                        added_count +=1
                    
                    except Exception as e:
                        errors.append({'row_index': index, 'data': mining_data, 'reason': str(e)})
            
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
        form = UploadMiningForm()
    return render(request,'general_data/transport_templates/upload_transport_form.html',{'form':form})