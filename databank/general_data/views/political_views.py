from datetime import datetime
from django.db import DataError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Q
import pandas as pd
from ..models import Political_Data, Country_meta
from ..forms import UploadLandData,UploadLandDataForm, UploadLandMetaForm
from trade_data.views import tables
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.views.decorators.http import require_POST

from trade_data import views

def is_valid_queryparam(param):
    return param !='' and param is not None


def display_political_table(request):

    data = Political_Data.objects.all()
    country_categories = Country_meta.objects.all()

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    country_category = request.GET.get('country_category')
    political_party_name = request.GET.get('political_party_name')    
    min_no_of_members = request.GET.get('minimum_no_of_members')
    max_no_of_members = request.GET.get('maximum_no_of_members')
    province = request.GET.get('view_province')
    district = request.GET.get('district')
    municipality = request.GET.get('municipality')
    ward = request.GET.get('ward')  

  

    if is_valid_queryparam(date_min):
        data=data.filter(Year__gte=date_min)

    if is_valid_queryparam(date_max):
        data=data.filter(Year__lt=date_max)

    if is_valid_queryparam(country_category) and country_category != '--':
        data = data.filter(Country_id=country_category)

    if is_valid_queryparam(political_party_name):
        data=data.filter(Q(Political_Party_Name__icontains=political_party_name)).distinct()

    if is_valid_queryparam(min_no_of_members):
        data = data.filter(Number_Of_Member__gte=min_no_of_members)

    if is_valid_queryparam(max_no_of_members):
        data = data.filter(Number_Of_Member__lt=max_no_of_members)

    if is_valid_queryparam(province):
        data=data.filter(Q(Province__icontains=province)).distinct()

    if is_valid_queryparam(district):
        data=data.filter(Q(District__icontains=district)).distinct()

    if is_valid_queryparam(municipality):
        data=data.filter(Q(Municipality__icontains=municipality)).distinct()

    if is_valid_queryparam(ward):
        data=data.filter(Q(Wards__icontains=ward)).distinct()

    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    

    context={
        'tables':tables,
        'data_len':len(data),
        'query_len': len(page),
        'page':page,
        'country_categories':country_categories,
    }
    return render(request, 'general_data/political_templates/political_table.html',context)