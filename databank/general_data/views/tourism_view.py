import datetime
from django.db import DataError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Q
import pandas as pd
from ..models import Tourism, Country_meta,Tourism_Meta
from ..forms import UploadForestDataForm,UploadTourismData
from trade_data.views import tables
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.views.decorators.http import require_POST


def is_valid_queryparam(param):
    return param !='' and param is not None


def display_tourism_table(request):

    url = reverse('tourism_table')
    data = Tourism.objects.all()
    country_categories = Country_meta.objects.all()
    arrival_codes = Tourism_Meta.objects.all()

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    arrival_mode = request.GET.get('arrival_mode')
    country_category = request.GET.get('country_category')
    nationality_category = request.GET.get('nationality_category')
    min_tourist = request.GET.get('minimum_tourist')
    max_tourist = request.GET.get('maximum_tourist')


    if is_valid_queryparam(date_min):
        data=data.filter(Year__gte=date_min)

    if is_valid_queryparam(date_max):
        data=data.filter(Year__lt=date_max)

    if is_valid_queryparam(country_category) and country_category != '--':
        data = data.filter(Country_id=country_category)

    if is_valid_queryparam(nationality_category) and nationality_category != '--':
        data = data.filter(Nationality_Of_Tourism_id=nationality_category)

    if is_valid_queryparam(arrival_mode) and arrival_mode != '--':
        data = data.filter(Arrival_code_id=arrival_mode)

    if is_valid_queryparam(min_tourist):
        data = data.filter(Number_Of_Tourist__gte=min_tourist)

    if is_valid_queryparam(max_tourist):
        data = data.filter(Number_Of_Tourist__lt=max_tourist)


    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    

    context={
        'tables':tables,
        'data_len':len(data),
        'page':page,
        'query_len': len(page),
        'country_categories':country_categories,
        'arrival_codes':arrival_codes,
        
    }
    return render(request, 'general_data/tourism_templates/tourism_table.html',context)

@require_POST
def delete_selected_tourism(request):
    selected_ids = request.POST.getlist('selected_items')
    if not selected_ids:
        messages.error(request, 'No items selected for deletion.')
        return redirect('tourism_table')
    try:
        Tourism.objects.filter(id__in=selected_ids).delete()
        messages.success(request, 'Selected items deleted successfully.')
    except Exception as e:
        messages.error(request, f'Error deleting items: {e}')

    return redirect('tourism_table')


def delete_tourism_record(request,item_id):
    try:
        item_to_delete = get_object_or_404(Tourism, id=item_id)
        item_to_delete.delete()
        messages.success(request, 'Deleted successfully')
        return redirect('tourism_table')
    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}")
    


def update_tourism_record(request,pk):
    tourism_record = Tourism.objects.get(id=pk)
    form = UploadTourismData(instance=tourism_record)

    if request.method == 'POST':
        form = UploadTourismData(request.POST, instance=tourism_record)
        if form.is_valid():
            form.save()
            return redirect('tourism_table')
        
    context={'form':form,}
    return render(request,'general_data/tourism_templates/update_tourism_record.html',context)