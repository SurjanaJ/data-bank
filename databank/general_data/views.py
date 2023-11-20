import datetime
from django.db import DataError
from django.http import HttpResponse
from django.shortcuts import render
from django.core.paginator import Paginator
from django.urls import reverse
import pandas as pd
from .models import ForestData, Country_meta
from .forms import UploadForestDataForm
from trade_data.views import tables


def upload_forest_excel(request):
    if request.method == 'POST':
        form = UploadForestDataForm(request.POST, request.FILES)
        if form.is_valid():
            excel_data = request.FILES['forest_data_file']
            df = pd.read_excel(excel_data)

            for index, row in df.iterrows():
                Country = row['Country']
                Year = row['Year']
                try:
                    Country = Country_meta.objects.get(Country_Name=Country)
                    
                # except (Country_meta.DoesNotExist, HS_Code_meta.DoesNotExist, Unit_meta.DoesNotExist):
                #     return HttpResponse('could not upload the file.')
                except DataError as e:
                    print(f"Error inserting row {index}: {e}")
                    print(f"Problematic row data: {row}")

                forest_data = ForestData (
                    Year = datetime.date(Year,1,1),
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

def display_forest_table(request):
    url=reverse('forest_table')
    data=ForestData.objects.all()
    country_categories=Country_meta.objects.all()
    stock_unit_categories=[choice[1] for choice in ForestData.Stock_Unit_Options]
    area_unit_categories=[choice[1] for choice in ForestData.Area_Unit_Options]

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