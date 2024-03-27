from datetime import datetime
from django.db import DataError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Q
import pandas as pd

from .energy_view import strip_spaces
from ..models import Road, Country_meta,Road_Meta
from ..forms import UploadRoadForm
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


def display_road_table(request):


    data = Road.objects.all()
    road_codes=Road_Meta.objects.all()
    length_unit_options = [choice[1] for choice in Road.Length_Unit ]

    country_categories = Country_meta.objects.all()

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    country_category = request.GET.get('country_category')
    road_code = request.GET.get('road_code')
    min_length = request.GET.get('minimum_length')
    max_length = request.GET.get('maximum_length')
    unit = request.GET.get('road_unit')
    Highway_No = request.GET.get('highway_no')
 

    if is_valid_queryparam(date_min):
        data=data.filter(Year__gte=date_min)

    if is_valid_queryparam(date_max):
        data=data.filter(Year__lt=date_max)

    if is_valid_queryparam(country_category) and country_category != '--':
        data = data.filter(Country_id=country_category)

    if is_valid_queryparam(road_code) and road_code != '--':
        data=data.filter(Code_Type_Of_Road = road_code)
     
    if is_valid_queryparam(min_length):
        data = data.filter(Length__gte=min_length)

    if is_valid_queryparam(max_length):
        data = data.filter(Length__lt=max_length)

    if is_valid_queryparam(unit)  and unit != '--':
        data=data.filter(Length_Unit_Options=unit) 

    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    

    context={
        'tables':tables,
        'data_len':len(data),
        'query_len': len(page),
        'page':page,
        'length_unit_options':length_unit_options,
        'country_categories':country_categories,
        'road_codes':road_codes,

    }
    return render(request, 'general_data/Road_templates/Road_table.html',context)



def upload_road_excel(request):
    errors=[]
    duplicate_data = []
    updated_count = 0
    added_count = 0

    if request.method == 'POST':
        form = UploadRoadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_data = request.FILES['file']
            df = pd.read_excel(excel_data,dtype={'Code':str})
            df.fillna('', inplace=True)
            df = df.map(strip_spaces)

            unit_options = [option[0] for option in Road.Length_Unit]

            if 'id' in df.columns:
                for index, row in df.iterrows():
                    id = row.get('id')
                    data = {
                        'Year':row['Year'],
                        'Country':row['Country'],
                        'Highway No':row['Highway No'],
                        'Name Of The Road':row['Name Of The Road'],
                        'Code':row['Code'],
                        'Road Type':row['Road Type'],
                        'Length Unit':row['Length Unit'],
                        'Length':row['Length']
                    }
                    try:
                        road_instance = Road.objects.get(id=id)
                        road_data = data

                        try:
                            country = Country_meta.objects.get(Country_Name=row['Country'])
                            code = Road_Meta.objects.get(Code = row['Code'])
                                
                            road_instance.Year = row['Year']
                            road_instance.Country=country
                            road_instance.Highway_No= row['Highway No']
                            road_instance.Name_Of_The_Road = row['Name Of The Road']
                            road_instance.Code_Type_Of_Road = code
                            road_instance.Length_Unit_Options=row['Length Unit']            
                            road_instance.Length = row['Length']

                            road_instance.save()
                            updated_count +=1
                        
                        except Exception as e:
                            road_data = data
                            errors.append({'row_index': index, 'data': road_data, 'reason': str(e)})
                            continue


                    except Exception as e:
                        road_data= data
                        errors.append({
                            'row_index':index,
                            'data':road_data,
                            'reason':f'Error inserting row {index}:{e}'
                        })
                        continue
                    
                    
            else:
                for index,row in df.iterrows():
                    data = {
                        'Year':row['Year'],
                        'Country':row['Country'],
                        'Highway No':row['Highway No'],
                        'Name Of The Road':row['Name Of The Road'],
                        'Code':row['Code'],
                        'Road Type':row['Road Type'],
                        'Length Unit':row['Length Unit'],
                        'Length':row['Length']
                    }
                    
                    try:
                        country = Country_meta.objects.get(Country_Name = row['Country'])
                        code = Road_Meta.objects.get(Code = row['Code'])
                        
                        existing_record = Road.objects.filter(
                            Q(Year = row['Year'] )
                            & Q(Country = country) 
                            & Q(Highway_No = row['Highway No']) 
                            & Q(Length_Unit_Options = row['Length Unit']) 
                            & Q(Code_Type_Of_Road = code) 
                            & Q(Length = row['Length'])
                            ).first()
                        
                        if existing_record:
                            road_data= data
                            duplicate_data.append({
                                'row_index':index,
                                'data': road_data,
                                'reason': 'Duplicate data found'
                            })

                        else:
                            try:
                                road_data = {
                                    'Year':row['Year'],
                                    'Country':country,
                                    'Highway_No':row['Highway No'],
                                    'Name_Of_The_Road':row['Name Of The Road'],
                                    'Code_Type_Of_Road':code,
                                    'Length_Unit_Options':row['Length Unit'],
                                    'Length':row['Length']
                                }
                                print('ROAD DATA')
                                print(road_data)

                                Roaddata = Road(**road_data)
                                Roaddata.save()
                                added_count +=1

                            except Exception as e:
                                errors.append(f"Error inserting row {index}: {e}")

                            
                    except Exception as e:
                        road_data = data
                        errors.append({'row_index': index, 'data': road_data, 'reason': str(e)})
                        continue


            if added_count > 0:
                messages.success(request, f'{added_count} records added')

            if updated_count > 0:
                messages.info(request, str(updated_count) + ' records updated.')


            if errors:
                request.session['errors'] = errors
                return render(request, 'trade_data/error_template.html', {'errors': errors, 'tables': tables, 'meta_tables': views.meta_tables, })

            if duplicate_data:
                return render(request, 'trade_data/duplicate_template.html', {'duplicate_data': duplicate_data, 'tables': tables, 'meta_tables': views.meta_tables,})
            
            else:
            # form is not valid
                return redirect('road_table') 

    else:
        form = UploadRoadForm()

    return render(request, 'general_data/upload_form.html', {'form': form, 'tables':tables})                            

def display_road_meta(request):
    data = Road_Meta.objects.all()
    total_data = data.count()

    column_names = Road_Meta._meta.fields

    context = {'data': data, 'total_data':total_data, 'meta_tables':views.meta_tables, 'tables':tables, 'column_names':column_names}
    return render(request, 'general_data/display_meta.html', context)


def update_selected_road(request):
    selected_ids = request.POST.getlist('selected_items')
    if not selected_ids:
        messages.error(request, 'No items selected.')
        return redirect('road_table')

    else:
        queryset = Road.objects.filter(id__in=selected_ids)
        queryset = queryset.annotate(
        country = F('Country__Country_Name'),
        code_type_of_road = F('Code_Type_Of_Road__Code'),
        road_type = F('Code_Type_Of_Road__Road_Type'),
        )

        df = pd.DataFrame(list(queryset.values('id','Year','country','Highway_No','Name_Of_The_Road','code_type_of_road','road_type','Length_Unit_Options','Length')))
        df.rename(columns={'country': 'Country','code_type_of_road':'Code','road_type':'Road Type','Highway_No':'Highway No','Name_Of_The_Road':'Name Of The Road','Length_Unit_Options':'Length Unit'}, inplace=True)
        df = df[['id','Year','Country','Highway No','Name Of The Road','Code','Road Type','Length Unit','Length']]
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