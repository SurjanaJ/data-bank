from .models import ForestData
from io import BytesIO
from . import views
import xlsxwriter
from django.db.models import Q
from django.db.models import F
import pandas as pd
from django.shortcuts import HttpResponse

def filter(request):
    data =ForestData.objects.all()

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    country_category = request.GET.get('country_category')
    name_of_the_plant = request.GET.get('name_of_the_plant')
    stock_available = request.GET.get('stock_available')
    area_unit = request.GET.get('area_unit')

    if views.is_valid_queryparam(date_min):
        data=data.filter(Year__gte=date_min)

    if views.is_valid_queryparam(date_max):
        data=data.filter(Year__lt=date_max)

    if views.is_valid_queryparam(name_of_the_plant):
        data=data.filter(Q(Name_Of_The_Plant__icontains=name_of_the_plant)).distinct()

    if views.is_valid_queryparam(country_category) and country_category != '--':
        data = data.filter(Country_id=country_category)

    if views.is_valid_queryparam(area_unit)  and area_unit != '--':
        data=data.filter(Area_Unit=area_unit)

    if views.is_valid_queryparam(stock_available):
        data=data.filter(Stock_Available__gte=stock_available)

    return data

def export_forest_table_to_excel(request):
    data=filter(request)

    data=data.annotate(
        country_name=F('Country__Country_Name'),
    )

    df=pd.DataFrame(data.values('Year','country_name','Name_Of_The_Plant','Scientific_Name','Local_Name','Stock_Unit','Stock_Available','Area_Unit','Area_Covered'))


    df.rename(columns={'country_name': 'Country'},inplace=True)

    df = df[['Year','Country','Name_Of_The_Plant','Scientific_Name','Local_Name','Stock_Unit','Stock_Available','Area_Unit','Area_Covered']]
    
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1', index=False)

    writer.close()
    output.seek(0)

    response = HttpResponse(
        output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=forest_table.xlsx'
    return response