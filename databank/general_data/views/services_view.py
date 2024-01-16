from django.shortcuts import render

from trade_data.models import Country_meta
from ..models import Services, Services_Meta
from trade_data import views
from trade_data.views import tables
from django.core.paginator import Paginator, Page


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


def display_services_table(request):
    data = Services.objects.all()
    column_names = Services._meta.fields

    country_categories = Country_meta.objects.all()
    direction_categories = [choice[1] for choice in Services.DIRECTION_OPTIONS]
    service_code = Services_Meta.objects.all()
    
    paginator = Paginator(data, 40)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = { 'data_len': len(data), 'country_categories': country_categories, 'direction_categories': direction_categories, 'service_code':service_code ,'page':page, 'query_len': len(page), 'tables':tables, 'meta_tables':views.meta_tables, 'column_names':column_names}

    return render(request, 'general_data/services_templates/services_table.html', context)
