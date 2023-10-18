from io import BytesIO
import pandas as pd
from django.http import HttpResponse
import xlsxwriter  # Import the XlsxWriter library

from .models import TradeData  # Import your model here

def export_to_excel(request):
    data = TradeData.objects.all()  

    df = pd.DataFrame(list(data.values()))
    
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')  # Use 'xlsxwriter' as the engine

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
