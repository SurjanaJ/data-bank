from datetime import datetime
from django.db import DataError
from django.forms import model_to_dict
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Q
import pandas as pd
from ..models import Housing, Country_meta,Housing_Meta
from ..forms import UploadHousingForm
from trade_data.views import tables
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import F
from io import BytesIO
from django.http import HttpResponse

from trade_data import views

def is_valid_queryparam(param):
    return param !='' and param is not None

def display_housing_table(request):

    data = Housing.objects.all()
    house_codes=Housing_Meta.objects.all()

    country_categories = Country_meta.objects.all()

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    country_category = request.GET.get('country_category')
    house_Code = request.GET.get('house_code')
    min_number = request.GET.get('minimum_number')  
    max_number = request.GET.get('maximum_number')
    name_of_the_city = request.GET.get('name_of_the_city')

  

    if is_valid_queryparam(date_min):
        data=data.filter(Year__gte=date_min)

    if is_valid_queryparam(date_max):
        data=data.filter(Year__lt=date_max)

    if is_valid_queryparam(country_category) and country_category != '--':
        data = data.filter(Country_id=country_category)

    if is_valid_queryparam(house_Code) and house_Code != '--':
        data=data.filter(House_Code = house_Code)

    if is_valid_queryparam(name_of_the_city):
        data=data.filter(Q(City__icontains=name_of_the_city)).distinct()

    if is_valid_queryparam(max_number):
        data = data.filter(Number__lt=max_number)   

    if is_valid_queryparam(min_number):
        data = data.filter(Number__gte=min_number)

    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    

    context={
        'tables':tables,
        'data_len':len(data),
        'query_len': len(page),
        'page':page,
        'country_categories':country_categories,
        'house_codes':house_codes,

    }
    return render(request, 'general_data/housing_templates/housing_table.html',context)

def upload_housing_excel(request):
    errors = []
    duplicate_data = []
    updated_count = 0
    added_count = 0

    if request.method == 'POST':
        form = UploadHousingForm(request.POST,request.FILES)
        if form.is_valid():
            excel_data = request.FILES['file']
            df = pd.read_excel(excel_data,dtype={'House_Code':str})
            df.fillna('',inplace=True)

            if 'id' in df.columns:
                cols = df.columns.to_list()
                for index, row in df.iterrows():
                    id_value = row.get('id')
                    try:
                        housing_instance = Housing.objects.get(id=id_value)
                    except Exception as e:
                        data = {col: row[col] for col in cols}
                        errors.append({
                            'row_index':index,
                            'data':data,
                            'reason':f'Error inserting row {index}:{e}'
                        })
                        continue
                    housing_data =  {
                        'Year':row['Year'],
                        'Country':row['Country'],
                        'House_Code':row['House_Code'],
                        'City':row['City'],
                        'Number':row['Number']
                    }

                    try:
                        country_instance = Country_meta.objects.get(Country_Name=row['Country'])
                        housing_id = Housing_Meta.objects.get(Code = row['House_Code'])
                        
                        housing_instance.Year = row['Year']
                        housing_instance.Country = country_instance
                        housing_instance.House_Code = housing_id
                        housing_instance.City = row['City']
                        housing_instance.Number = row['Number']
                        housing_instance.save()

                        updated_count +=1

                    except Exception as e:
                        housing_data = {
                            'Year':row['Year'],
                            'Country':row['Country'],
                            'House_Code':row['House_Code'],
                            'City':row['City'],
                            'Number':row['Number']
                        }
                        errors.append({'row_index':index,'data':housing_data,'reason':str(e)})
                        continue

            else:
                for index,row in df.iterrows():
                    housing_data =  {
                        'Year':row['Year'],
                        'Country':row['Country'],
                        'House_Code':row['House_Code'],
                        'City':row['City'],
                        'Number':row['Number']
                    }
                    Country = None
                    try:
                        country_instance = Country_meta.objects.get(Country_Name = row['Country'])
                        housing_code = Housing_Meta.objects.get(Code = row['House_Code'])

                        housing_data = {
                            'Year':row['Year'],
                            'Country':country_instance,
                            'House_Code':housing_code,
                            'City':row['City'],
                            'Number':row['Number']
                        }
                    except Exception as e:
                        errors.append({'row_index':index,'data':housing_data,'reason':str(e)})
                        continue

                    existing_record = Housing.objects.filter(
                        Q(Country=country_instance ) & Q(Year = housing_data['Year']) & Q(House_Code = housing_code) & Q(City = housing_data['City']) & Q(Number=housing_data['Number'])
                    ).first()
                    print(existing_record)

                    if existing_record:
                            housing_data = {
                                'Year':row['Year'],
                                'Country':Country,
                                'House_Code':housing_code,
                                'City':row['City'],
                                'Number':row['Number']
                            }
                            duplicate_data.append({
                                'row_index':index,
                                'data':{key:str(value)for key,value in housing_data.items()}
                            })

                    else:
                        try:
                            HousingData = Housing(**housing_data)
                            HousingData.save()
                            added_count +=1
                        
                        except Exception as e:
                            errors.append({'row_index': index, 'data': housing_data, 'reason': str(e)})

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
                return redirect('housing_table')
    else:
        form = UploadHousingForm()
    return render(request,'general_data/transport_templates/upload_transport_form.html',{'form':form})

def display_housing_meta(request):
    data = Housing_Meta.objects.all()
    total_data = data.count()

    column_names = Housing_Meta._meta.fields

    context = {'data': data, 'total_data':total_data, 'meta_tables':views.meta_tables, 'tables':tables, 'column_names':column_names}
    return render(request, 'general_data/display_meta.html', context)

def update_selected_housing(request):
    selected_ids = request.POST.getlist('selected_items')
    if not selected_ids:
        messages.error(request, 'No items selected.')
        return redirect('housing_table')

    else:
        queryset = Housing.objects.filter(id__in=selected_ids)
        queryset = queryset.annotate(
        country = F('Country__Country_Name'),
        house_code = F('House_Code__Code'),
        house_type = F('House_Code__House_Type'),
        )

        df = pd.DataFrame(list(queryset.values('id','Year','country','house_code','house_type','City','Number')))
        df.rename(columns={'country': 'Country','house_code':'House_Code','house_type':'House_Type'}, inplace=True)
        df = df[['id','Year','Country','House_Code','House_Type','City','Number']]
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