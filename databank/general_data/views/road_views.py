from datetime import datetime
from django.db import DataError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Q
import pandas as pd
from ..models import Road, Country_meta,Road_Meta
from ..forms import UploadLandData,UploadLandDataForm, UploadLandMetaForm
from trade_data.views import tables
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.views.decorators.http import require_POST

from trade_data import views

def is_valid_queryparam(param):
    return param !='' and param is not None


def display_road_table(request):

    data = Road.objects.all()
    road_codes=Road_Meta.objects.all()
    length_unit_options = [choice[1] for choice in Road.Length_Unit ]

    country_categories = Country_meta.objects.all()

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    country_category = request.GET.get('country_category')
    road_code = request.GET.get('road_code')
    min_length = request.GET.get('minimum_length')
    max_length = request.GET.get('maximum_length')
    unit = request.GET.get('road_unit')
    Highway_No = request.GET.get('highway_no')
 

    if is_valid_queryparam(date_min):
        data=data.filter(Year__gte=date_min)

    if is_valid_queryparam(date_max):
        data=data.filter(Year__lt=date_max)

    if is_valid_queryparam(country_category) and country_category != '--':
        data = data.filter(Country_id=country_category)

    if is_valid_queryparam(road_code) and road_code != '--':
        data=data.filter(Code_Type_Of_Road = road_code)
     
    if is_valid_queryparam(min_length):
        data = data.filter(Length__gte=min_length)

    if is_valid_queryparam(max_length):
        data = data.filter(Length__lt=max_length)

    if is_valid_queryparam(unit)  and unit != '--':
        data=data.filter(Length_Unit_Options=unit) 

    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    

    context={
        'tables':tables,
        'data_len':len(data),
        'query_len': len(page),
        'page':page,
        'length_unit_options':length_unit_options,
        'country_categories':country_categories,
        'road_codes':road_codes,

    }
    return render(request, 'general_data/Road_templates/Road_table.html',context)