from io import BytesIO
from django.db import IntegrityError
from django.forms import model_to_dict
from django.shortcuts import redirect, render
import pandas as pd
from django.contrib import messages
from django.core.paginator import Paginator

from ..models import Production_Meta, Production
from .energy_view import strip_spaces
from trade_data.models import Country_meta, Unit_meta
from trade_data.views import is_valid_queryparam, tables
from django.http import HttpResponse
from django.db.models import F, Q
from trade_data import views

def display_production_meta(request):
    data = Production_Meta.objects.all()
    total_data = data.count()

    column_names = Production_Meta._meta.fields

    context = {'data': data, 'total_data':total_data, 'meta_tables':views.meta_tables, 'tables':tables, 'column_names':column_names}
    
    return render(request, 'general_data/display_meta.html', context)

def display_production_table(request):
    data = Production.objects.all()

    production_categories = Production_Meta.objects.all()

    code = request.GET.get('code')
    if is_valid_queryparam(code) and code != '--':
        data = data.filter(Code_id=code)

    
    paginator = Paginator(data, 40)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context ={'data_len':len(data),
              'page':page, 
              'query_len':len(page), 
              'tables': tables, 
              'meta_tables': views.meta_tables,
              'production_categories':production_categories,
                      }
    return render(request, 'general_data/production_templates/production_table.html', context)
