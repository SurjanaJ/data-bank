from django.shortcuts import render
from trade_data import views
from ..models import Crime_Meta
from trade_data.views import is_valid_queryparam, tables

def display_crime_meta(request):
    data = Crime_Meta.objects.all()
    total_data = data.count()

    column_names = Crime_Meta._meta.fields

    context = {'data': data, 'total_data':total_data, 'meta_tables':views.meta_tables, 'tables':tables, 'column_names':column_names}
    
    return render(request, 'general_data/display_meta.html', context)