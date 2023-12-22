import datetime
from django.db import DataError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Q
import pandas as pd
from ..models import Land, Country_meta,Land_Code_Meta
from ..forms import UploadLandData,UploadLandDataForm
from trade_data.views import tables
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.views.decorators.http import require_POST


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
    land_code = request.GET.get('land_code')
    unit = request.GET.get('land_unit')
    min_value = request.GET.get('minimum_area')
    max_value = request.GET.get('maximum_area')

  

    if is_valid_queryparam(date_min):
        data=data.filter(Year__gte=date_min)

    if is_valid_queryparam(date_max):
        data=data.filter(Year__lt=date_max)

    if is_valid_queryparam(land_code) and land_code != '--':
        data=data.filter(Land_Code = land_code)
     

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
    return render(request,'general_data/land_templates/update_land_record.html',context)


def upload_land_excel(request):
    if request.method == 'POST':
        form = UploadLandDataForm(request.POST,request.FILES)
        if form.is_valid():
            excel_data = request.Files['land_data_file']
            df = pd.read_excel(excel_data)

            errors = []
            duplicate_data = []
            updated_count = 0
            added_count = 0

            if 'id' in df.columns or 'ID' in df.columns:
                for index,row in df.iterrows():
                    id_value = row['ID']

                    try:
                        land_instance = Land.objects.get(id = id_value)
                    except:
                        land_instance=Land()

                    Year = row['Year']
                    Country = row['Country']
                    land_code = row['land_Code']

                    try:
                        calender_year = datetime.strptime(str(row['Year']),'%Y-%m-%d').date()
                    except ValueError:
                        calender_year = datetime.strptime(f'{str(row["Year"])}-01-01','%Y-%m-%d').date()


                    try:
                        Year = calender_year.strftime('%Y-%m-%d')
                        country = Country_meta.objects.get(Country_Name = Country)
                        land_code = Land_Code_Meta.objects.get(Code = land_code)
                        
                    except DataError as e:
                        print(f"error handling the row at {index}:{e}")
                        continue

                    land_instance.Year = Year
                    land_instance.Country = country
                    land_instance.Land_Code = land_code
                    land_instance.Unit = row['Unit']
                    land_instance.Area = row['Area']
                    land_instance.save()

                    updated_count +=1

                else:
                    for index,row in df.iterrows():

                        land_data={
                            'Year': row['Year'].date().strftime('%Y-%m-%d'),
                            'Country': row['Country'],
                            'land_code': row['land_Code'],
                            'Unit': row['Unit'],
                            'Area': row['Area']
                        }

                        try:
                            calender_date = datetime.strptime(str(row['Year'].date().strftime('%Y-%m-%d')), '%Y-%m-%d').date()
                        except ValueError:
                            calender_date = datetime.strptime(f'{str(row["Year"].date().strftime("%Y-%m-%d"))}-01-01', '%Y-%m-%d').date()

                        try:
                            Year = calender_date.strftime('%Y-%m-%d')
                            Country = Country_meta.objects.get(Country_Name=row['Country'])
                            land_code = Land_Code_Meta.objects.get(Code = land_code)

                            land_data={
                                'Year': row['Year'].date().strftime('%Y-%m-%d'),
                                'Country': row['Country'],
                                'land_code': row['land_Code'],
                                'Unit': row['Unit'],
                                'Area': row['Area']
                            }

                        except Exception as e:
                            errors.append({'row_index': index, 'data': population_data, 'reason': str(e)})
                            continue

                        
        

    