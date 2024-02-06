from datetime import datetime
from django.db import DataError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Q
import pandas as pd
from ..models import Land, Country_meta,Land_Code_Meta
from ..forms import UploadLandData,UploadLandDataForm, UploadLandMetaForm
from trade_data.views import tables
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.views.decorators.http import require_POST

from trade_data import views

def is_valid_queryparam(param):
    return param !='' and param is not None


def display_land_table(request):

    data = Land.objects.all()
    land_codes=Land_Code_Meta.objects.all()

    country_categories = Country_meta.objects.all()
    Land_Unit_Options = [choice[1] for choice in Land.Land_Unit_Options]

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    country_category = request.GET.get('country_category')
    Land_Code = request.GET.get('land_code')
    unit = request.GET.get('land_unit')
    min_value = request.GET.get('minimum_area')
    max_value = request.GET.get('maximum_area')

  

    if is_valid_queryparam(date_min):
        data=data.filter(Year__gte=date_min)

    if is_valid_queryparam(date_max):
        data=data.filter(Year__lt=date_max)

    if is_valid_queryparam(Land_Code) and Land_Code != '--':
        data=data.filter(Land_Code = Land_Code)
     

    if is_valid_queryparam(country_category) and country_category != '--':
        data = data.filter(Country_id=country_category)
        

    if is_valid_queryparam(unit)  and unit != '--':
        data=data.filter(Unit=unit)

    if is_valid_queryparam(min_value):
        data = data.filter(Area__gte=min_value)

    if is_valid_queryparam(max_value):
        data = data.filter(Area__lt=max_value)


    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    

    context={
        'tables':tables,
        'data_len':len(data),
        'query_len': len(page),
        'page':page,
        'country_categories':country_categories,
        'Land_Unit_Options':Land_Unit_Options,
        'land_codes':land_codes,

    }
    return render(request, 'general_data/land_templates/land_table.html',context)

@require_POST
def delete_selected_land(request):
    selected_ids = request.POST.getlist('selected_items')
    if not selected_ids:
        messages.error(request, 'No items selected for deletion.')
        return redirect('land_table')
    try:
        Land.objects.filter(id__in=selected_ids).delete()
        messages.success(request, 'Selected items deleted successfully.')
    except Exception as e:
        messages.error(request, f'Error deleting items: {e}')

    return redirect('land_table')


def delete_land_record(request,item_id):
    try:
        item_to_delete = get_object_or_404(Land, id=item_id)
        item_to_delete.delete()
        messages.success(request, 'Deleted successfully')
        return redirect('land_table')
    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}")

    
def update_land_record(request,pk):
    land_record = Land.objects.get(id=pk)
    form = UploadLandData(instance=land_record)

    if request.method == 'POST':
        form = UploadLandData(request.POST, instance=land_record)
        if form.is_valid():
            form.save()
            return redirect('land_table')
        
    context={'form':form,}
    return render(request,'general_data/update_record.html',context)


def upload_land_excel(request):
    errors = []
    duplicate_data = []
    updated_count = 0
    added_count = 0
    
    if request.method == 'POST':
        form = UploadLandDataForm(request.POST,request.FILES)
        
        if form.is_valid():
            excel_data = request.FILES['Land_data_file']
            df = pd.read_excel(excel_data)

            if 'id' in df.columns or 'ID' in df.columns:
                for index,row in df.iterrows():
                    id_value = row['ID']

                    try:
                        land_instance = Land.objects.get(id = id_value)
                    except:
                        land_instance=Land()

                        
                    Year = row['Year']
                    Country = row['Country']
                    Land_Code = row['Land_Code']

                    try:
                        calender_year = pd.to_datetime(Year).date()
                    except ValueError as e:
                        print(f"Error converting date in row {index}: {e}")
                        print(f"Problematic row data: {row}")
                        continue
                    try:
                        Year = calender_year
                        country = Country_meta.objects.get(Country_Name = Country)
                        Land_Code = Land_Code_Meta.objects.get(Code = Land_Code)
                        
                    except DataError as e:
                        print(f"error handling the row at {index}:{e}")
                        continue

                    land_instance.Year = Year
                    land_instance.Country = country
                    land_instance.Land_Code = Land_Code
                    land_instance.Unit = row['Unit']
                    land_instance.Area = row['Area']
                    land_instance.save()

                    updated_count +=1
            else:

                land_unit_options = [option[0] for option in Land.Land_Unit_Options]

                for index,row in df.iterrows():
                    land_data={
                        'Year': row['Year'].date().strftime('%Y-%m-%d'),
                        'Country': row['Country'],
                        'Land_Code': row['Land_Code'],
                        'Unit': row['Unit'],
                        'Area': row['Area']
                    }

                    if land_data['Unit'] not in land_unit_options:
                        errors.append({
                            'row_index': index,
                            'data': land_data,
                            'reason': f'Error inserting row {index}: Invalid unit value'
                        })

                    else:
                        try:
                            calender_date = datetime.strptime(str(row['Year'].date().strftime('%Y-%m-%d')), '%Y-%m-%d').date()
                            
                        except ValueError:
                            calender_date = datetime.strptime(f'{str(row["Year"].date().strftime("%Y-%m-%d"))}-01-01', '%Y-%m-%d').date()

                        Country = None

                        try:
                            Year = calender_date.strftime('%Y-%m-%d')
                            Country = Country_meta.objects.get(Country_Name=row['Country'])
                            Land_Code = Land_Code_Meta.objects.get(Code = row['Land_Code'])
                            
                            land_data={
                                'Year': Year,
                                'Country': Country.Country_Name,
                                'Land_Code':Land_Code.Code,
                                'Unit': row['Unit'],
                                'Area': row['Area']
                            }                           

                        except Exception as e:
                            errors.append({
                                'row_index': index,
                                'data': land_data, 
                                'reason': f'Error inserting row  {index}: {e}'
                            })
                            continue

                        existing_record = Land.objects.filter(Q(Year = Year) & Q(Country = Country) & Q(Land_Code = Land_Code) & Q(Unit = land_data['Unit']) & Q(Area = land_data['Area'])).first()

                        if existing_record:
                                duplicate_data.append({
                                    'row_index' :index,
                                    'data': land_data,
                                    'reason': 'Duplicate record found'
                                })       
                            
                        else:
                            try:
                                LandData = Land(**land_data)
                                LandData.save()
                                added_count +=1

                            except Exception as e:
                                errors.append({
                                    'row_index': index,
                                    'data': land_data,
                                    'reason': f'Error inserting row  {index}: {e}'
                                })
            if added_count> 0 :
                messages.success(request,str(added_count)+ 'records addad')
                                
            if updated_count > 0:
                messages.info(request,str(updated_count)+'records updated') 

            if errors:
                request.session['errors'] = errors
                return render(request, 'general_data/error_template.html', {'errors': errors})

            if duplicate_data:
                return render (request,'general_data/duplicate_template.html',{'duplicate_data':duplicate_data})      
              
    else:
        form = UploadLandDataForm()
    return render(request,'general_data/land_templates/upload_land_form.html',{'form':form})
        
def display_land_meta(request):
    data = Land_Code_Meta.objects.all()
    total_data = data.count()

    column_names = Land_Code_Meta._meta.fields

    context = {'data': data, 'total_data':total_data, 'meta_tables':views.meta_tables, 'tables':tables, 'column_names':column_names}
    return render(request, 'general_data/display_meta.html', context)
