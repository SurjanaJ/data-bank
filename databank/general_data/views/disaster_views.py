from datetime import datetime
from django.db import DataError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.core.paginator import Paginator
from django.forms import model_to_dict
from django.db.models import Q
import pandas as pd
from ..models import Disaster_Data, Country_meta,Disaster_Data_Meta
from ..forms import UploadDisasterForm
from trade_data.views import tables
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.views.decorators.http import require_POST

from trade_data import views

def is_valid_queryparam(param):
    return param !='' and param is not None


def display_disaster_table(request):

    data = Disaster_Data.objects.all()

    disaster_codes=Disaster_Data_Meta.objects.all()

    country_categories = Country_meta.objects.all()

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    country_category = request.GET.get('country_category')
    disaster_Code = request.GET.get('disaster_code')
    min_human_loss = request.GET.get('minimum_human_loss')
    max_human_loss = request.GET.get('maximum_human_loss')
    min_animal_loss = request.GET.get('minimum_animal_loss')
    max_animal_loss = request.GET.get('maximum_animal_loss')
    min_property_loss = request.GET.get('minimum_property_loss')
    max_property_loss = request.GET.get('maximum_property_loss')


    if is_valid_queryparam(date_min):
        data=data.filter(Year__gte=date_min)

    if is_valid_queryparam(date_max):
        data=data.filter(Year__lt=date_max)

    if is_valid_queryparam(disaster_Code) and disaster_Code != '--':
        data=data.filter(Disaster_Code = disaster_Code)

    if is_valid_queryparam(country_category) and country_category != '--':
        data = data.filter(Country_id=country_category)

    if is_valid_queryparam(min_human_loss):
        data = data.filter(Human_Loss__gte=min_human_loss)

    if is_valid_queryparam(max_human_loss):
        data = data.filter(Human_Loss__lt=max_human_loss)

    if is_valid_queryparam(min_animal_loss):
        data = data.filter(Animal_Loss__gte=min_animal_loss)

    if is_valid_queryparam(max_animal_loss):
        data = data.filter(Animal_Loss__lt=max_animal_loss)

    if is_valid_queryparam(min_property_loss):
        data = data.filter(Physical_Properties_Loss_In_USD__gte=min_property_loss)

    if is_valid_queryparam(max_property_loss):
        data = data.filter(Physical_Properties_Loss_In_USD__lt=max_property_loss)

    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    

    context={
        'tables':tables,
        'data_len':len(data),
        'query_len': len(page),
        'page':page,
        'country_categories':country_categories,
        'disaster_codes':disaster_codes,

    }
    return render(request, 'general_data/disaster_templates/disaster_table.html',context)


def upload_disaster_excel(request):
    errors = []
    duplicate_data = []
    updated_count = 0
    added_count = 0

    if request.method == 'POST':
        form = UploadDisasterForm(request.POST,request.FILES)
        if form.is_valid():
            excel_data = request.FILES['file']
            df = pd.read_excel(excel_data,dtype={'Disaster_id':str})
            cols = df.columns.to_list()
            df.fillna('',inplace=True)


            for index,row in df.iterrows():
                disaster_data = {col: row[col] for col in cols}
                
                try:
                    Country_instance = Country_meta.objects.get(Country_Name = row['Country'])
                    disaster_id = Disaster_Data_Meta.objects.get(Code = row['Disaster_id'])
                    disaster_data = {
                        'Year':row['Year'],
                        'Country':Country_instance,
                        'Disaster_Code':disaster_id,
                        'Human_Loss':row['Human_Loss'],
                        'Animal_Loss':row['Animal_Loss'],
                        'Physical_Properties_Loss_In_USD':row['Physical_Properties_Loss_In_USD']
                        
                    }
                    
                except Exception as e:
                    errors.append({'row_index':index, 'data':disaster_data , 'reason': str(e)})
                    continue

                
                existing_record = Disaster_Data.objects.filter(Q(Year = row['Year'] )& Q(Country = Country_instance) & Q(Disaster_Code = disaster_id)).first()

                if existing_record:
                    existing_dict = model_to_dict(existing_record)
                    disaster_data_dict = model_to_dict(Disaster_Data(**disaster_data))

                    if all(existing_dict[key] == disaster_data_dict[key] or (pd.isna(existing_dict[key])and pd.isna(disaster_data_dict[key])) for key in disaster_data_dict if key != 'id' ):
                        disaster_data = {
                            'Year':row['Year'],
                            'Country':Country_instance,
                            'Disaster_Code':disaster_id.Code,
                            'Human_Loss':row['Human_Loss'],
                            'Animal_Loss':row['Animal_Loss'],
                            'Physical_Properties_Loss_In_USD':row['Physical_Properties_Loss_In_USD']
                        }
                        duplicate_data.append({
                            'row_index':index,
                            'data':{key:str(value)for key,value in disaster_data.items()}
                        })
                    
                    else:
                        for key ,value in disaster_data.items():
                            setattr(existing_record,key ,  value)
                        try:
                            existing_record.save()
                            updated_count +=1

                        except IntegrityError  as e:
                            errors.append({'row_index': index, 'data': disaster_data, 'reason': str(e)})

                else:
                    try:
                        DisasterData = Disaster_Data(**disaster_data)
                        DisasterData.save()
                        added_count +=1
                    
                    except Exception as e:
                        errors.append({'row_index': index, 'data': disaster_data, 'reason': str(e)})

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
                return redirect('disaster_table')
    else:
        form = UploadDisasterForm()
    return render(request,'general_data/transport_templates/upload_transport_form.html',{'form':form})


