from datetime import datetime
from django.db import DataError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Q
import pandas as pd
from ..models import Tourism, Country_meta,Tourism_Meta
from ..forms import UploadTourismDataForm,UploadTourismData
from trade_data.views import tables
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.views.decorators.http import require_POST

from trade_data import views


def is_valid_queryparam(param):
    return param !='' and param is not None


def display_tourism_table(request):
    url = reverse('tourism_table')
    data = Tourism.objects.all()
    country_categories = Country_meta.objects.all()
    arrival_codes = Tourism_Meta.objects.all()

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    arrival_mode = request.GET.get('arrival_mode')
    country_category = request.GET.get('country_category')
    nationality_category = request.GET.get('nationality_category')
    min_tourist = request.GET.get('minimum_tourist')
    max_tourist = request.GET.get('maximum_tourist')


    if is_valid_queryparam(date_min):
        data=data.filter(Year__gte=date_min)

    if is_valid_queryparam(date_max):
        data=data.filter(Year__lt=date_max)

    if is_valid_queryparam(country_category) and country_category != '--':
        data = data.filter(Country_id=country_category)

    if is_valid_queryparam(nationality_category) and nationality_category != '--':
        data = data.filter(Nationality_Of_Tourism_id=nationality_category)

    if is_valid_queryparam(arrival_mode) and arrival_mode != '--':
        data = data.filter(Arrival_code_id=arrival_mode)

    if is_valid_queryparam(min_tourist):
        data = data.filter(Number_Of_Tourist__gte=min_tourist)

    if is_valid_queryparam(max_tourist):
        data = data.filter(Number_Of_Tourist__lt=max_tourist)


    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    

    context={
        'tables':tables,
        'data_len':len(data),
        'page':page,
        'query_len': len(page),
        'country_categories':country_categories,
        'arrival_codes':arrival_codes,
        
    }
    return render(request, 'general_data/tourism_templates/tourism_table.html',context)

@require_POST
def delete_selected_tourism(request):
    selected_ids = request.POST.getlist('selected_items')
    if not selected_ids:
        messages.error(request, 'No items selected for deletion.')
        return redirect('tourism_table')
    try:
        Tourism.objects.filter(id__in=selected_ids).delete()
        messages.success(request, 'Selected items deleted successfully.')
    except Exception as e:
        messages.error(request, f'Error deleting items: {e}')

    return redirect('tourism_table')


def delete_tourism_record(request,item_id):
    try:
        item_to_delete = get_object_or_404(Tourism, id=item_id)
        item_to_delete.delete()
        messages.success(request, 'Deleted successfully')
        return redirect('tourism_table')
    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}")
 
def update_tourism_record(request,pk):
    tourism_record = Tourism.objects.get(id=pk)
    form = UploadTourismData(instance=tourism_record)

    if request.method == 'POST':
        form = UploadTourismData(request.POST, instance=tourism_record)
        if form.is_valid():
            form.save()
            return redirect('tourism_table')
        
    context={'form':form,}
    return render(request,'general_data/tourism_templates/update_tourism_record.html',context)

def upload_tourism_excel(request):
    errors = []
    duplicate_data = []
    updated_count = 0
    added_count = 0


    if request.method == 'POST':
        form = UploadTourismDataForm(request.POST,request.FILES)

        if form.is_valid():
            excel_data = request.FILES['Tourism_data_file']
            df = pd.read_excel(excel_data)

            if 'id' in df.columns or 'ID' in df.columns:
                for index,row in df.iterrows():
                    id_value = row['ID']

                    try:
                        tourism_instance = Tourism.objects.get(id = id_value)
                    except:
                        tourism_instance = Tourism()

                    Year = row['Year']
                    Country = row['Country']
                    Nationality_Of_Tourism = row['Nationality_Of_Tourism']
                    Arrival_Mode = row['Arrival_Mode']

                    try:
                        calender_year =pd.to_datetime(Year).date()
                    except ValueError as e:
                        print(f"Error converting date in row {index}: {e}")
                        print(f"Problematic row data: {row}")
                        continue

                    try:
                        Year = calender_year 
                        Country = Country_meta.objects.get(Country_Name = Country)
                        Nationality_Of_Tourism = Country_meta.objects.get(Country_Name = Nationality_Of_Tourism)
                        Arrival_Mode = Tourism_Meta.objects.get(Code = Arrival_Mode)
                    except DataError as e:
                        print(f'error handling the row at {index}:{e}')
                        continue

                    tourism_instance.Year = Year
                    tourism_instance.Country = Country
                    tourism_instance.Number_Of_Tourist = row['Number_Of_Tourist']
                    tourism_instance.Nationality_Of_Tourism= Nationality_Of_Tourism
                    tourism_instance.Arrival_code = Arrival_Mode
                    tourism_instance.Number = row['Number']

                    tourism_instance.save()
                    updated_count +=1

            else:
                for index,row in df.iterrows():
                    tourism_data ={
                        'Year':row['Year'].date(),
                        'Country': row['Country'],
                        'Number_Of_Tourist': row['Number_Of_Tourist'],
                        'Nationality_Of_Tourism':row['Nationality_Of_Tourism'],
                        'Arrival_Mode':row['Arrival_Mode'],
                        'Number': row['Number']
                    }
                    try:
                        calender_date = pd.to_datetime(Year).date()
                    except:
                        calender_date = datetime.strptime(f'{str(row["Year"].date().strftime("%Y-%m-%d"))}-01-01', '%Y-%m-%d').date()

                    Country = None
                    Arrival_Mode =None
                    Nationality_Of_Tourism = None


                    try:
                        Year = calender_date.strftime('%Y-%m-%d')
                        Country = Country_meta.objects.get(Country_Name=row['Country'])
                        Nationality_Of_Tourism = Country_meta.objects.get(Country_Name = row['Nationality_Of_Tourism'])
                        Arrival_Mode = Tourism_Meta.objects.get(Code = row['Arrival_Mode'])

                        tourism_data = {
                            'Year':Year,
                            'Country':Country,
                            'Number_Of_Tourist': row['Number_Of_Tourist'],
                            'Nationality_Of_Tourism':Nationality_Of_Tourism,
                            'Arrival_Mode':Arrival_Mode,
                            'Number':row['Number']    
                        }

                    except Exception as e:
                        errors.append({
                            'row_index': index,
                            'data': tourism_data,
                            'reason':  f'Error inserting row  {index}: {e}'
                        })
                        continue
                        

                    existing_record = Tourism.objects.filter(Q(Year = Year) & Q(Country = Country) & Q(Nationality_Of_Tourism = Nationality_Of_Tourism) & Q(Arrival_code = Arrival_Mode)).first()

                    if existing_record:
                        duplicate_data.append({
                            'row_index':index,
                            'data':tourism_data,
                            'reason': 'Duplicate record found'
                        })

                    else:
                        try:
                            TourismData = Tourism(**tourism_data)
                            TourismData.save()

                            added_count +=1

                        except Exception as e:
                            errors.append({
                                'row_index': index,
                                'data': tourism_data,
                                'reason':f'Error inserting row {index}:{e}'
                            })
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
        form = UploadTourismDataForm()

    return render(request,'general_data/tourism_templates/upload_tourism_form.html',{'form':form})

def display_tourism_meta(request):
    data = Tourism_Meta.objects.all()
    total_data = data.count()

    column_names = Tourism_Meta._meta.fields

    context = {'data': data, 'total_data':total_data, 'meta_tables':views.meta_tables, 'tables':tables, 'column_names':column_names}
    return render(request, 'general_data/display_meta.html', context)
