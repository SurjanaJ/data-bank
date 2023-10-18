from io import BytesIO
import pandas as pd
from django.http import HttpResponse
import xlsxwriter  # Import the XlsxWriter library
from django.db.models import F

from .models import TradeData  

def export_to_excel(request):
    data = TradeData.objects.all()  
    
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
