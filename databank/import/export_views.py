from io import BytesIO
import pandas as pd
from django.http import HttpResponse
import xlsxwriter  # Import the XlsxWriter library
from django.db.models import Q
from django.db.models import F
from django.db.models import Sum

from . import views
from .models import TradeData  


def filter(request):
    data = TradeData.objects.all()
    
    # get data from html
    currency_product_originDestination_query = request.GET.get('currency_product_originDestination')
    quantity_min = request.GET.get('quantity_min')
    quantity_max = request.GET.get('quantity_max')
    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    country_category = request.GET.get('country_category')
    unit_category = request.GET.get('unit_category')
    hs_code = request.GET.get('hs_code')
    trade_type = request.GET.get('trade_type')
    
    # filter the trade data given by user
    if views.is_valid_queryparam(currency_product_originDestination_query):
        data = data.filter(
            Q(Currency_Type__icontains = currency_product_originDestination_query)  | Q(Origin_Destination__icontains = currency_product_originDestination_query) ).distinct()
        
    if views.is_valid_queryparam(quantity_min):
        data = data.filter(Quantity__gte=quantity_min)

    if views.is_valid_queryparam(quantity_max):
        data = data.filter(Quantity__lt=quantity_max)
 
    if views.is_valid_queryparam(date_min):
        data = data.filter(Calender__gte = date_min)

    if views.is_valid_queryparam(date_max):
        data = data.filter(Calender__lt = date_max)

    if views.is_valid_queryparam(country_category) and country_category != '--':
        data = data.filter(Origin_Destination_id=country_category)
    
    if views.is_valid_queryparam(unit_category) and unit_category != '--':
        data = data.filter(Unit=unit_category)

    if views.is_valid_queryparam(hs_code) and hs_code != '--':
        data = data.filter(HS_Code=hs_code)

    if views.is_valid_queryparam(trade_type) and trade_type != '--':
        data = data.filter(Trade_Type=trade_type) 
    
    return data

def export_to_excel(request):
    data = filter(request)
    
    # getting the foreign key values
    data = data.annotate(
        country_name=F('Country__Country_Name'),  
        hs_code_name=F('HS_Code__HS_Code'),  
        unit_name=F('Unit__Unit_Code'),  
        origin_destination_name=F('Origin_Destination__Country_Name'),  
        product_information = F('HS_Code__Product_Information')
    )

    # selecting the values to display
    df = pd.DataFrame(data.values('Trade_Type', 'Calender', 'Fiscal_Year', 'Duration', 'country_name', 'hs_code_name', 'product_information', 'unit_name', 'Quantity', 'Currency_Type', 'Amount', 'Tarrif', 'origin_destination_name', 'TradersName_ExporterImporter', 'DocumentsLegalProcedural'))

    # renaming the columns to match the original model
    df.rename(columns={'country_name': 'Country', 'hs_code_name': 'HS_Code', 'unit_name':'Unit','origin_destination_name':'Origin_Destination','product_information':'Product_Information'}, inplace=True)
    
    
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')  # Use 'xlsxwriter' as the engine
    df.to_excel(writer, sheet_name='Sheet1', index=False)

    writer.close()  
    output.seek(0)

    # Create the HttpResponse object with appropriate header
    response = HttpResponse(
        output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=exported_data.xlsx'
    return response


def trade_record_to_excel(request):
    data = TradeData.objects.all()

    country_category = request.GET.get('country_category')
    hs_code = request.GET.get('hs_code')
    trade_type = request.GET.get('trade_type')

    if views.is_valid_queryparam(country_category) and country_category != '--':
        data = data.filter(Origin_Destination_id=country_category)

    if views.is_valid_queryparam(hs_code) and hs_code != '--':
        data = data.filter(HS_Code_id=hs_code)

    if views.is_valid_queryparam(trade_type) and trade_type != '--':
        data = data.filter(Trade_Type=trade_type)


    if not data.exists():
        return HttpResponse("No data to export")

    # Retrieve the years and data for the table
    years = set(data.values_list('Calender__year', flat=True).distinct())

    if country_category != '--' and country_category is not None:
        # Filter for the specific case where 'country_category' is selected
        df = data.values('HS_Code_id__HS_Code', 'Calender__year', 'Amount').annotate(
            year_amount=Sum('Amount')
        ).order_by('HS_Code_id', 'Calender__year')
    else:
        # Filter for the case where 'country_category' is not selected
        df = data.values('Origin_Destination__Country_Name', 'Calender__year', 'Amount').annotate(
            year_amount=Sum('Amount')
        ).order_by('Origin_Destination__Country_Name', 'Calender__year')

    # Convert QuerySet to a Pandas DataFrame
    df = pd.DataFrame.from_records(df)

    # Pivot the DataFrame
    df = df.pivot(index='HS_Code_id__HS_Code' if country_category != '--' else 'Origin_Destination__Country_Name',
                  columns='Calender__year', values='year_amount')

    df = df.reset_index()
    df.fillna(0, inplace=True)


    # Rename columns to "Exported value in <year>"
    df.columns = [""] + ["Exported value in {}".format(col) for col in df.columns[1:]]

    # Create an in-memory Excel writer object
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')

    # Convert the DataFrame to an XlsxWriter Excel object
    df.to_excel(writer, sheet_name='Sheet1', index=False)

    writer.close()
    output.seek(0)

    # Create the HttpResponse object with appropriate header
    response = HttpResponse(
        output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=exported_data.xlsx'
    return response