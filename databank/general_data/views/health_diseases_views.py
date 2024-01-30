from datetime import datetime
from django.db import DataError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Q
import pandas as pd
from ..models import Health_disease, Country_meta,Health_disease_Meta
from ..forms import UploadForestDataForm,UploadForestData, UploadLandMetaForm, UploadTourismMetaForm, UploadTransportMetaForm, UploadWaterMetaForm
from trade_data.views import tables
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.views.decorators.http import require_POST


def is_valid_queryparam(param):
    return param !='' and param is not None


def display_health_disease_table(request):
    data=Health_disease.objects.all()
    country_categories=Country_meta.objects.all()
    health_disease_codes=Health_disease_Meta.objects.all()

    unit_categories=[choice[1] for choice in Health_disease.Unit_Options]


    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    country_category = request.GET.get('country_category')
    unit=request.GET.get('unit')
    disease_code = request.GET.get('health_disease_code')
    minimum_number = request.GET.get('minimum_number')
    maximum_number = request.GET.get('maximum_number')

    if is_valid_queryparam(date_min):
        data=data.filter(Year__gte=date_min)

    if is_valid_queryparam(date_max):
        data=data.filter(Year__lt=date_max)

    if is_valid_queryparam(country_category) and country_category != '--':
        data = data.filter(Country_id=country_category)

    if is_valid_queryparam(unit)  and unit != '--':
        data=data.filter(Unit=unit)

    if is_valid_queryparam(minimum_number):
        data=data.filter(Number_Of_Case__gte=minimum_number)

    if is_valid_queryparam(maximum_number):
        data=data.filter(Number_Of_Case__lt=maximum_number)

    #get form data for filteration

    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context={
        'data_len':len(data),
        'query_len': len(page),
        'page':page,    
        'country_categories':country_categories,
        'unit_categories':unit_categories,
        'health_disease_codes':health_disease_codes,
        'tables':tables
    }

    return render(request, 'general_data/health_disease_templates/health_disease_table.html',context)
