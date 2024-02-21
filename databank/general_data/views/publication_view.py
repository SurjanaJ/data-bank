from io import BytesIO
from django.db import IntegrityError
from django.forms import model_to_dict
from django.shortcuts import redirect, render
import pandas as pd
from django.contrib import messages
from django.core.paginator import Paginator
from trade_data.models import Country_meta, Unit_meta
from trade_data.views import is_valid_queryparam, tables
from django.http import HttpResponse
from django.db.models import F, Q
from trade_data import views

from ..models import Publication


def display_publication_table(request):
    data = Publication.objects.all()
    country_categories = Country_meta.objects.all()

    country = request.GET.get('country')
    year_min = request.GET.get('year_min')
    year_max = request.GET.get('year_max')

    if is_valid_queryparam(year_min):
        data = data.filter(Year__gte=year_min)

    if is_valid_queryparam(year_max):
        data = data.filter(Year__lt=year_max)  

    if is_valid_queryparam(country) and country != '--':
        data = data.filter(Country_id=country)  

    paginator = Paginator(data, 40)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context ={'data_len':len(data),
              'page':page, 
              'query_len':len(page), 
              'tables': tables, 
              'meta_tables': views.meta_tables,
              'country_categories':country_categories,
                      }
    return render(request, 'general_data/publication_templates/publication_table.html', context)
    