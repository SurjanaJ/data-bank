from datetime import datetime
from django.db import DataError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Q
import pandas as pd
from ..models import Housing, Country_meta,Housing_Meta
from ..forms import UploadLandData,UploadLandDataForm, UploadLandMetaForm
from trade_data.views import tables
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.views.decorators.http import require_POST

from trade_data import views

def is_valid_queryparam(param):
    return param !='' and param is not None


def display_housing_table(request):

    data = Housing.objects.all()
    house_codes=Housing_Meta.objects.all()

    country_categories = Country_meta.objects.all()

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    country_category = request.GET.get('country_category')
    disaster_Code = request.GET.get('disaster_code')
    min_human_loss = request.GET.get('minimum_human_loss')  
    max_human_loss = request.GET.get('maximum_human_loss')
    min_animal_loss = request.GET.get('minimum_animal_loss')
    max_animal_loss = request.GET.get('maximum_animal_loss')
    min_property_loss = request.GET.get('minimum_physical_property_loss_in_usd')
    max_property_loss = request.GET.get('maximum_physical_property_loss_in_usd')

  

    if is_valid_queryparam(date_min):
        data=data.filter(Year__gte=date_min)

    if is_valid_queryparam(date_max):
        data=data.filter(Year__lt=date_max)

    if is_valid_queryparam(disaster_Code) and disaster_Code != '--':
        data=data.filter(Disaster_Code = disaster_Code)
     

    if is_valid_queryparam(country_category) and country_category != '--':
        data = data.filter(Country_id=country_category)

    if is_valid_queryparam(min_human_loss):
        data = data.filter(Human_Loss__gte=min_human_loss)

    if is_valid_queryparam(max_human_loss):
        data = data.filter(Human_Loss__lt=max_human_loss)

    if is_valid_queryparam(min_animal_loss):
        data = data.filter(Animal_Loss__gte=min_animal_loss)

    if is_valid_queryparam(max_animal_loss):
        data = data.filter(Animal_Loss__lt=max_animal_loss)

    if is_valid_queryparam(min_property_loss):
        data = data.filter(Physical_Properties_Loss_In_USD__gte=min_property_loss)

    if is_valid_queryparam(max_property_loss):
        data = data.filter(Physical_Properties_Loss_In_USD__lt=max_property_loss)

    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    

    context={
        'tables':tables,
        'data_len':len(data),
        'query_len': len(page),
        'page':page,
        'country_categories':country_categories,
        'house_codes':house_codes,

    }
    return render(request, 'general_data/housing_templates/housing_table.html',context)