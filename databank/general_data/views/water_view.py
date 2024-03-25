from datetime import datetime
from django.db import DataError

from django.shortcuts import get_object_or_404, render,redirect
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Q
import pandas as pd
from ..models import Water, Country_meta,Water_Meta
from ..forms import UploadWaterDataForm,UploadWaterData
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


def display_water_table(request):

    data = Water.objects.all()
    country_categories = Country_meta.objects.all()
    water_options = Water_Meta.objects.all()
    unit_options = [choice[1] for choice in Water.Unit_Options]

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')

    country_category = request.GET.get('country_category')
    water_code = request.GET.get('water_code')
    name_of_the_river = request.GET.get('name_of_the_river')
    unit=request.GET.get('unit')
    min_volume = request.GET.get('minimum_volume')
    max_volume = request.GET.get('maximum_volume')

    if is_valid_queryparam (date_min):
        data=data.filter(Year__gte=date_min)

    if is_valid_queryparam(date_max):
        data=data.filter(Year__lte=date_max)

    if is_valid_queryparam(country_category) and country_category != '--':
        data = data.filter(Country_id=country_category)

    if is_valid_queryparam(water_code) and water_code != '--':
        data = data.filter(Water_Type_Code_id=water_code)

    if is_valid_queryparam(unit) and unit != '--':
        data = data.filter(Unit=unit)


    if is_valid_queryparam(name_of_the_river):
        data=data.filter(Q(Name_Of_The_River__icontains=name_of_the_river)).distinct()

    if is_valid_queryparam(min_volume):
        data = data.filter(Volume__gte=min_volume)

    if is_valid_queryparam(max_volume):
        data = data.filter(Volume__lt=max_volume)

    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    

    context={
        'tables':tables,
        'data_len':len(data),
        'page':page,
        'query_len': len(page),
        'country_categories':country_categories,
        'water_options':water_options,
        'unit_options':unit_options,

    }
    return render(request, 'general_data/water_templates/water_table.html',context)

@require_POST
def delete_selected_water(request):
    selected_ids = request.POST.getlist('selected_items')
    if not selected_ids:
        messages.error(request, 'No items selected for deletion.')
        return redirect('water_table')
    try:
        Water.objects.filter(id__in=selected_ids).delete()
        messages.success(request, 'Selected items deleted successfully.')
    except Exception as e:
        messages.error(request, f'Error deleting items: {e}')

    return redirect('water_table')


def delete_water_record(request,item_id):
    try:
        item_to_delete = get_object_or_404(Water, id=item_id)
        item_to_delete.delete()
        messages.success(request, 'Deleted successfully')
        return redirect('water_table')
    except Exception as e:
        messages.error(request, f'Error deleting items: {e}')


# def update_water_record(request,pk):
#     water_record = Water.objects.get(id=pk)
#     form = UploadWaterData(instance=water_record)

#     if request.method == 'POST':
#         form = UploadWaterData(request.POST, instance=water_record)
#         if form.is_valid():
#             form.save()
#             return redirect('water_table')
        
#     context={'form':form,}
#     return render(request,'general_data/water_templates/update_water_record.html',context)



def upload_water_excel(request):
    errors = []
    duplicate_data = []
    updated_count = 0
    added_count = 0


    if request.method == 'POST':
        form = UploadWaterDataForm(request.POST,request.FILES)

        if form.is_valid():
            excel_data = request.FILES['Water_data_file']
            df = pd.read_excel(excel_data,dtype={'Water Type Code':str})
            water_unit_options = [option[0] for option in Water.Unit_Options]
            
            if 'id' in df.columns:
                for index,row in df.iterrows():
                    id = row.get('id') 
                    data ={
                        'Year':row['Year'],
                        'Country':row['Country'],
                        'Water_Type_Code':row['Water Type Code'],
                        'Water_Type':row['Water Type'],
                        'Description':row['Description'],
                        'Unit':row['Unit'],
                        'Volume':row['Volume'],
                        'Name_Of_The_River':row['Name Of The River'],
                    }
                    try:
                        water_instance = Water.objects.get(id = id)
                        water_data = data

                        try:
                            Country = Country_meta.objects.get(Country_Name = row['Country'])
                            Water_Type_Code = Water_Meta.objects.get(Code = row['Water Type Code'])

                            water_instance.Country = Country
                            water_instance.Water_Type_Code = Water_Type_Code
                            water_instance.Year = row['Year']
                            water_instance.Description = row['Description']
                            water_instance.Unit = row['Unit']
                            water_instance.Volume= row['Volume']
                            water_instance.Name_Of_The_River = row['Name Of The River']

                            water_instance.save()
                            updated_count +=1

                        except Exception as e:
                            water_data= data
                            errors.append({'row_index': index, 'data': water_data, 'reason': str(e)})
                            continue

                    except Exception as e:
                        water_data= data
                        errors.append({
                            'row_index':index,
                            'data':water_data,
                            'reason':f'Error inserting row {index}:{e}'
                        })
                        continue
                        
            else:
                for index, row in df.iterrows():
                    data ={
                        'Year':row['Year'],
                        'Country':row['Country'],
                        'Water_Type_Code':row['Water Type Code'],
                        'Water_Type':row['Water Type'],
                        'Description':row['Description'],
                        'Unit':row['Unit'],
                        'Volume':row['Volume'],
                        'Name_Of_The_River':row['Name Of The River'],
                    }

                    try:
                            Country = Country_meta.objects.get(Country_Name = row['Country'])
                            Water_Type_Code = Water_Meta.objects.get(Code = row['Water Type Code'])

                            water_data ={
                                'Year':row['Year'],
                                'Country':Country,
                                'Water_Type_Code':Water_Type_Code,
                                'Description':row['Description'],
                                'Unit':row['Unit'],
                                'Volume':row['Volume'],
                                'Name_Of_The_River':row['Name Of The River'],
                            }
                            existing_record =Water.objects.filter(
                                Q(Country = Country) 
                                & Q(Year = row['Year']) 
                                & Q(Water_Type_Code = Water_Type_Code)
                                & Q(Description = row['Description'])
                                & Q(Unit = row['Unit'])
                                & Q(Volume = row['Volume'])
                                & Q(Name_Of_The_River = row['Name Of The River'])
                            ).first()

                            if existing_record:
                                water_data = data
                                duplicate_data.append({
                                    'row_index': index,
                                        'data': {key: str(value) for key, value in water_data.items()}
                                })
                                continue
                        
                        # add new record
                            else:
                                try:
                                    waterData = Water(**water_data)
                                    waterData.save()
                                    added_count += 1
                                except Exception as e:
                                    errors.append(f"Error inserting row {index}: {e}")
                    
                    except Exception as e:
                        water_data = data
                        errors.append({'row_index': index, 'data': water_data, 'reason': str(e)})
                        continue        

                # Update the success messages
            if added_count > 0:
                messages.success(request, f'{added_count} records added')

            if updated_count > 0:
                    messages.success(request, f'{updated_count} records updated')

            if errors:
                request.session['errors'] = errors
                return render(request, 'general_data/error_template.html', {'errors': errors})

            if duplicate_data:
                return render(request, 'general_data/duplicate_template.html', {'duplicate_data': duplicate_data})
            
            else:
                return redirect('water_table')

    else:
        form = UploadWaterDataForm()

    return render(request,'general_data/water_templates/upload_water_form.html',{'form':form})

def display_water_meta(request):
    data = Water_Meta.objects.all()
    total_data = data.count()

    column_names = Water_Meta._meta.fields

    context = {'data': data, 'total_data':total_data, 'meta_tables':views.meta_tables, 'tables':tables, 'column_names':column_names}
    return render(request, 'general_data/display_meta.html', context)


def update_selected_water(request):
    selected_ids = request.POST.getlist('selected_items')
    if not selected_ids:
        messages.error(request, 'No items selected.')
        return redirect('water_table')

    else:
        queryset = Water.objects.filter(id__in=selected_ids)
        queryset = queryset.annotate(
        country = F('Country__Country_Name'),
        water_code = F('Water_Type_Code__Code'),
        water_type = F('Water_Type_Code__Water_Type'),
        )

        df = pd.DataFrame(list(queryset.values('id','Year','country','water_code','water_type','Description','Unit','Volume','Name_Of_The_River')))
        df.rename(columns={'country': 'Country','water_code':'Water Type Code','water_type':'Water Type','Name_Of_The_River':'Name Of The River'}, inplace=True)
        df = df[['id','Year','Country','Water Type Code','Water Type','Description','Unit','Volume','Name Of The River']]
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