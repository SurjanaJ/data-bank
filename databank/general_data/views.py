import datetime
from django.db import DataError
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Q
import pandas as pd
from .models import ForestData, Country_meta
from .forms import UploadForestDataForm,UpdateForestData
from trade_data.views import tables

def is_valid_queryparam(param):
    return param !='' and param is not None
    

def upload_forest_excel(request):
    if request.method == 'POST':
        form = UploadForestDataForm(request.POST, request.FILES)
        if form.is_valid():
            excel_data = request.FILES['forest_data_file']
            df = pd.read_excel(excel_data)

            for index, row in df.iterrows():
                Country = row['Country']
                Year = str(row['Year'])
                Name_Of_The_Plant=row['Name_Of_The_Plant']

                try:
                    Country = Country_meta.objects.get(Country_Name=Country)
                    
                # except (Country_meta.DoesNotExist, HS_Code_meta.DoesNotExist, Unit_meta.DoesNotExist):
                #     return HttpResponse('could not upload the file.')
                except DataError as e:
                    print(f"Error inserting row {index}: {e}")
                    print(f"Problematic row data: {row}")
                
                try:
                    if len(Year) == 4:
                        Year = datetime.date(int(Year), 1, 1)
                    else:
                        Year = pd.to_datetime(Year).date()
                except ValueError as e:
                    print(f"Error converting date in row {index}: {e}")
                    print(f"Problematic row data: {row}")
                    # Handle the date conversion error, such as logging a message or skipping the row
                    continue

                existing_forest_data = ForestData.objects.filter(
                    Year=Year,
                    Country=Country,
                    Name_Of_The_Plant=Name_Of_The_Plant
                ).first()

                if existing_forest_data:
                    update_existing_record(existing_forest_data, row)
                    # Handle duplicate data, such as logging a message or skipping the row
                    print(request, f"updated data found for Year '{Year}', Country '{Country}', Name_Of_The_Plant '{Name_Of_The_Plant}'")
                    continue
                
                forest_data = ForestData (
                    Year = Year,
                    Country = Country,
                    Name_Of_The_Plant=row['Name_Of_The_Plant'],
                    Scientific_Name=row['Scientific_Name'],
                    Local_Name=row['Local_Name'],
                    Stock_Unit=row['Stock_Unit'],
                    Stock_Available=row['Stock_Available'],
                    Area_Unit=row['Area_Unit'],
                    Area_Covered=row['Area_Covered'],
                )
                forest_data.save()

            return HttpResponse('success')

    else:
        form = UploadForestDataForm()

    return render(request, 'general_data/upload_form.html', {'form': form, 'tables':tables})

def update_existing_record(existing_record, row):
    existing_record.Scientific_Name = row['Scientific_Name']
    existing_record.Local_Name = row['Local_Name']
    existing_record.Stock_Unit = row['Stock_Unit']
    existing_record.Stock_Available = row['Stock_Available']
    existing_record.Area_Unit = row['Area_Unit']
    existing_record.Area_Covered = row['Area_Covered']
    existing_record.save()


def update_forest_record(request,pk):
    forest_record = ForestData.objects.get(id=pk)
    form = UpdateForestData(instance=forest_record)

    if request.method == 'POST':
        form = UpdateForestData(request.POST, instance=forest_record)
        if form.is_valid():
            form.save()
            return redirect('forest_table')
        
    context={'form':form,}
    return render(request,'general_data/update_forest_record.html',context)

def delete_selected_records(request):
    if request.method == 'POST':
        selected_record_ids = request.POST.getlist('selected_records')
        ForestData.objects.filter(id__in=selected_record_ids).delete()

    return redirect('forest_table')


def display_forest_table(request):
    url=reverse('forest_table')
    data=ForestData.objects.all()
    country_categories=Country_meta.objects.all()
    stock_unit_categories=[choice[1] for choice in ForestData.Stock_Unit_Options]
    area_unit_categories=[choice[1] for choice in ForestData.Area_Unit_Options]


    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')

    country_category = request.GET.get('country_category')
    name_of_the_plant=request.GET.get('name_of_the_plant')
    area_unit=request.GET.get('area_unit')  
    stock_available=request.GET.get('stock_available')

    if is_valid_queryparam(date_min):
        data=data.filter(Year__gte=date_min)

    if is_valid_queryparam(date_max):
        data=data.filter(Year__lt=date_max)

    if is_valid_queryparam(name_of_the_plant):
        data=data.filter(Q(Name_Of_The_Plant__icontains=name_of_the_plant)).distinct()

    if is_valid_queryparam(country_category) and country_category != '--':
        data = data.filter(Country_id=country_category)

    if is_valid_queryparam(area_unit)  and area_unit != '--':
        data=data.filter(Area_Unit=area_unit)

    if is_valid_queryparam(stock_available):
        data=data.filter(Stock_Available__gte=stock_available)
        
    


    #get form data for filteration

    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context={
        'query_len': len(page),
        'page':page,
        'country_categories':country_categories,
        'stock_unit_categories':stock_unit_categories,
        'area_unit_categories':area_unit_categories,
        'tables':tables
    }

    return render(request, 'general_data/forest_table.html', context)