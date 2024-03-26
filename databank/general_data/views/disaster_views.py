from django.shortcuts import render,redirect
from django.core.paginator import Paginator
from django.db.models import Q
import pandas as pd

from .energy_view import strip_spaces
from ..models import Disaster_Data,Country_meta,Disaster_Data_Meta
from ..forms import UploadDisasterForm
from trade_data.views import tables
from django.contrib import messages
from django.db.models import F
from io import BytesIO
from django.http import HttpResponse
from trade_data import views
from django.contrib.auth.decorators import login_required
from accounts.decorators import allowed_users

def is_valid_queryparam(param):
    return param !='' and param is not None

@login_required(login_url = 'login')
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

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def upload_disaster_excel(request):
    errors = []
    duplicate_data = []
    updated_count = 0
    added_count = 0

    if request.method == 'POST':
        form = UploadDisasterForm(request.POST,request.FILES)
        if form.is_valid():
            excel_data = request.FILES['file']
            df = pd.read_excel(excel_data,dtype={'Disaster Code':str})
            df.fillna('',inplace=True)
            df = df.map(strip_spaces)

            # Check if required columns exist
            required_columns = ['Year', 'Country', 'Disaster Code','Human Loss','Animal Loss','Physical Properties Loss In USD']  # Add your required column names here
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                errors.append(f"Missing columns: {', '.join(missing_columns)}")
                return render(request,'general_data/invalid_upload.html', {'missing_columns': missing_columns, 'tables': tables, 'meta_tables': views.meta_tables,} )
            

            if 'id' in df.columns:
                for index, row in df.iterrows():
                    id = row.get('id')
                    data ={
                        'Year':row['Year'],
                        'Country':row['Country'],
                        'Disaster Code':row['Disaster Code'],
                        'Disaster Type':row['Disaster Type'],
                        'Human Loss':row['Human Loss'],
                        'Animal Loss':row['Animal Loss'],
                        'Physical Properties Loss In USD':row['Physical Properties Loss In USD']
                    }
                    try:
                        disaster_instance = Disaster_Data.objects.get(id=id)
                        disaster_data = data

                        try:
                            Country = Country_meta.objects.get(Country_Name=row['Country'])
                            Code = Disaster_Data_Meta.objects.get(Code = row['Disaster Code'])
                    
                            disaster_instance.Year = row['Year']
                            disaster_instance.Country = Country
                            disaster_instance.Disaster_Code =Code
                            disaster_instance.Human_Loss = row['Human Loss']
                            disaster_instance.Animal_Loss = row['Animal Loss']
                            disaster_instance.Physical_Properties_Loss_In_USD = row['Physical Properties Loss In USD']
                            
                            disaster_instance.save()
                            updated_count +=1
                        
                        except Exception as e:
                            disaster_data = data
                            errors.append({'row_index': index, 'data': disaster_data, 'reason': str(e)})
                            continue

                    except Exception as e:
                        disaster_data = data
                        errors.append({
                            'row_index':index,
                            'data':disaster_data,
                            'reason':f'Error inserting row {index}:{e}'
                        })
                        continue


            else:
                for index,row in df.iterrows():   
                    data ={
                        'Year':row['Year'],
                        'Country':row['Country'],
                        'Disaster Code':row['Disaster Code'],
                        'Disaster Type':row['Disaster Type'],
                        'Human Loss':row['Human Loss'],
                        'Animal Loss':row['Animal Loss'],
                        'Physical Properties Loss In USD':row['Physical Properties Loss In USD']
                    }
                                        
                    try:
                        Country = Country_meta.objects.get(Country_Name = row['Country'])
                        Code = Disaster_Data_Meta.objects.get(Code = row['Disaster Code'])
                        
                        existing_record = Disaster_Data.objects.filter(
                            Q(Year = row['Year'])
                            &Q(Country = Country)
                            &Q(Disaster_Code = Code)
                            &Q(Human_Loss = row['Human Loss'])
                            &Q(Animal_Loss = row['Animal Loss'])
                            &Q(Physical_Properties_Loss_In_USD = row['Physical Properties Loss In USD'])
                        ).first()

                        if existing_record:
                            disaster_data = data
                            duplicate_data.append({
                                    'row_index':index,
                                    'data':{key:str(value)for key,value in disaster_data.items()}
                            })
                            continue
                        else:
                            try:
                                disaster_data ={
                                    'Year':row['Year'],
                                    'Country':Country,
                                    'Disaster_Code':Code,
                                    'Human_Loss':row['Human Loss'],
                                    'Animal_Loss':row['Animal Loss'],
                                    'Physical_Properties_Loss_In_USD':row['Physical Properties Loss In USD']
                                }
                                DisasterData = Disaster_Data(**disaster_data)
                                DisasterData.save()
                                added_count +=1
                            
                            except Exception as e:
                                disaster_data = data
                                errors.append(f"Error inserting row {index}: {e}")

                    except Exception as e:
                        disaster_data = data
                        errors.append({'row_index': index, 'data': disaster_data, 'reason': str(e)})
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
                return render(request, 'trade_data/duplicate_template.html', {'duplicate_data': duplicate_data})
            else:
                return redirect('disaster_table')
    else:
        form = UploadDisasterForm()
    return render(request,'general_data/transport_templates/upload_transport_form.html',{'form':form})

@login_required(login_url = 'login')
def display_disaster_data_meta(request):
    data = Disaster_Data_Meta.objects.all()
    total_data = data.count()

    column_names = Disaster_Data_Meta._meta.fields

    context = {'data': data, 'total_data':total_data, 'meta_tables':views.meta_tables, 'tables':tables, 'column_names':column_names}
    return render(request, 'general_data/display_meta.html', context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
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
        disaster_type = F('Disaster_Code__Disaster_Type'),
        )

        df = pd.DataFrame(list(queryset.values('id','Year','country','disaster_code','disaster_type','Human_Loss','Animal_Loss','Physical_Properties_Loss_In_USD')))
        df.rename(columns={'country': 'Country', 'disaster_code': 'Disaster Code','disaster_type':'Disaster Type','Human_Loss':'Human Loss','Animal_Loss':'Animal Loss','Physical_Properties_Loss_In_USD':'Physical Properties Loss In USD'}, inplace=True)
        df = df[['id','Year','Country','Disaster Code','Disaster Type','Human Loss','Animal Loss','Physical Properties Loss In USD']]
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

