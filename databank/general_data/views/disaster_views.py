from django.shortcuts import render,redirect
from django.core.paginator import Paginator
from django.db.models import Q
import pandas as pd
from ..models import Disaster_Data,Country_meta,Disaster_Data_Meta
from ..forms import UploadDisasterForm
from trade_data.views import tables
from django.contrib import messages
from django.db.models import F
from io import BytesIO
from django.http import HttpResponse
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
            df.fillna('',inplace=True)

            if 'id' in df.columns:
                cols = df.columns.to_list()
                for index, row in df.iterrows():
                    id_value = row.get('id')
                    try:
                        disaster_instance = Disaster_Data.objects.get(id=id_value)
                    except Exception as e:
                        data = {col: row[col] for col in cols}
                        errors.append({
                            'row_index':index,
                            'data':data,
                            'reason':f'Error inserting row {index}:{e}'
                        })
                        continue
                    disaster_data = {
                        'Year':row['Year'],
                        'Country':row['Country'],
                        'Disaster_Code':row['Disaster_id'],
                        'Human_Loss':row['Human_Loss'],
                        'Animal_Loss':row['Animal_Loss'],
                        'Physical_Properties_Loss_In_USD':row['Physical_Properties_Loss_In_USD']
                    }
                    try:
                        country_instance = Country_meta.objects.get(Country_Name=row['Country'])
                        disaster_id = Disaster_Data_Meta.objects.get(Code = row['Disaster_id'])
                
                        disaster_instance.Year = row['Year']
                        disaster_instance.Country = country_instance
                        disaster_instance.Disaster_Code =disaster_id
                        disaster_instance.Human_Loss = row['Human_Loss']
                        disaster_instance.Animal_Loss = row['Animal_Loss']
                        disaster_instance.Physical_Properties_Loss_In_USD = row['Physical_Properties_Loss_In_USD']
                        disaster_instance.save()

                        updated_count +=1
                    except Exception as e:
                        disaster_data = {
                            'Year':row['Year'],
                            'Country':row['Country'],
                            'Disaster_Code':row['Disaster_id'],
                            'Human_Loss':row['Human_Loss'],
                            'Animal_Loss':row['Animal_Loss'],
                            'Physical_Properties_Loss_In_USD':row['Physical_Properties_Loss_In_USD']
                        }

                        errors.append({'row_index': index, 'data': disaster_data, 'reason': str(e)})
                        continue
                    
                    
            else:
                for index,row in df.iterrows():   
                    disaster_data = {
                        'Year':row['Year'],
                        'Country':row['Country'],
                        'Disaster_Code':row['Disaster_id'],
                        'Human_Loss':row['Human_Loss'],
                        'Animal_Loss':row['Animal_Loss'],
                        'Physical_Properties_Loss_In_USD':row['Physical_Properties_Loss_In_USD']
                    }
                                        
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
                    
                    existing_record = Disaster_Data.objects.filter(Q(Year = row['Year'] )& Q(Country = Country_instance) & Q(Disaster_Code = disaster_id) & Q(Human_Loss=row['Human_Loss']) & Q(Human_Loss=row['Human_Loss']) &Q( Animal_Loss = row['Animal_Loss']) & Q(Physical_Properties_Loss_In_USD=row['Physical_Properties_Loss_In_USD'])).first()

                    if existing_record:
                            duplicate_data.append({
                                'row_index':index,
                                'data':{key:str(value)for key,value in disaster_data.items()}
                            })
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

def display_disaster_data_meta(request):
    data = Disaster_Data_Meta.objects.all()
    total_data = data.count()

    column_names = Disaster_Data_Meta._meta.fields

    context = {'data': data, 'total_data':total_data, 'meta_tables':views.meta_tables, 'tables':tables, 'column_names':column_names}
    return render(request, 'general_data/display_meta.html', context)


def update_selected_disaster(request):
    selected_ids = request.POST.getlist('selected_items')
    if not selected_ids:
        messages.error(request, 'No items selected.')
        return redirect('disaster_table')

    else:
        queryset = Disaster_Data.objects.filter(id__in=selected_ids)
        queryset = queryset.annotate(
        country = F('Country__Country_Name'),
        disaster_code = F('Disaster_Code__Code'),
        )

        df = pd.DataFrame(list(queryset.values('id','Year','country','disaster_code','Human_Loss','Animal_Loss','Physical_Properties_Loss_In_USD')))
        df.rename(columns={'country': 'Country', 'disaster_code': 'Disaster_id'}, inplace=True)
        df = df[['id','Year','Country','Disaster_id','Human_Loss','Animal_Loss','Physical_Properties_Loss_In_USD']]
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

def update_selected_disaster(request):
    selected_ids = request.POST.getlist('selected_items')
    if not selected_ids:
        messages.error(request, 'No items selected.')
        return redirect('disaster_table')

    else:
        queryset = Disaster_Data.objects.filter(id__in=selected_ids)
        queryset = queryset.annotate(
        country = F('Country__Country_Name'),
        disaster_code = F('Disaster_Code__Code')
        )

        df = pd.DataFrame(list(queryset.values('id','Year','country','disaster_code','Human_Loss','Animal_Loss','Physical_Properties_Loss_In_USD')))
        df.rename(columns={'country': 'Country', 'disaster_code':'Disaster_id'}, inplace=True)
        df = df[['id','Year','Country','Disaster_id','Human_Loss','Animal_Loss','Physical_Properties_Loss_In_USD']]
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