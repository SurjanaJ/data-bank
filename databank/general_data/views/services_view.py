from django.shortcuts import render
from ..models import Services_Meta
from trade_data import views
from trade_data.views import tables


def display_services_meta(request):
    data = Services_Meta.objects.all()
    total_data = data.count()

    column_names = Services_Meta._meta.fields

    for item in data:
        for field in item._meta.fields: 
            print(field.name)
            print()
    context = {'data': data, 'total_data':total_data, 'meta_tables':views.meta_tables, 'tables':tables, 'column_names':column_names}
    
    return render(request, 'general_data/display_meta.html', context)