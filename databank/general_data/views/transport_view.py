import datetime
from django.db import DataError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Q
import pandas as pd
from ..models import Transport, Country_meta,Transport_Meta
from ..forms import UploadForestDataForm,UploadTransportData
from trade_data.views import tables
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.views.decorators.http import require_POST


def is_valid_queryparam(param):
    return param !='' and param is not None


def display_transport_table(request):

    url = reverse('transport_table')
    data = Transport.objects.all()
    country_categories = Country_meta.objects.all()
    unit_options = [choice[1] for choice in Transport.Unit_Options]
    transport_classification_codes = Transport_Meta.objects.all()

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')

    country_category = request.GET.get('country_category')
    transport_classification_code = request.GET.get('transport_classification_code')

    quantity_unit=request.GET.get('quantity_unit')
    min_quantity = request.GET.get('minimum_quantity')
    max_quantity = request.GET.get('maximum_quantity')

    if is_valid_queryparam(date_min):
        data=data.filter(Year__gte=date_min)

    if is_valid_queryparam(date_max):
        data=data.filter(Year__lt=date_max)

    if is_valid_queryparam(country_category) and country_category != '--':
        data = data.filter(Country_id=country_category)

    if is_valid_queryparam(transport_classification_code) and transport_classification_code != '--':
        data = data.filter(Transport_Classification_Code_id=transport_classification_code)

    if is_valid_queryparam(quantity_unit) and quantity_unit != '--':
        data = data.filter(Unit=quantity_unit)

    if is_valid_queryparam(min_quantity):
        data = data.filter(Quantity__gte=min_quantity)

    if is_valid_queryparam(max_quantity):
        data = data.filter(Quantity__lt=max_quantity)



    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    

    context={
        'tables':tables,
        'data_len':len(data),
        'page':page,
        'query_len': len(page),
        'country_categories':country_categories,
        'unit_options':unit_options,
        'transport_classification_codes':transport_classification_codes
    }
    return render(request, 'general_data/transport_templates/transport_table.html',context)

@require_POST
def delete_selected_transport(request):
    selected_ids = request.POST.getlist('selected_items')
    if not selected_ids:
        messages.error(request, 'No items selected for deletion.')
        return redirect('transport_table')
    try:
        Transport.objects.filter(id__in=selected_ids).delete()
        messages.success(request, 'Selected items deleted successfully.')
    except Exception as e:
        messages.error(request, f'Error deleting items: {e}')

    return redirect('transport_table')


def delete_transport_record(request,item_id):
    try:
        item_to_delete = get_object_or_404(Transport, id=item_id)
        item_to_delete.delete()
        messages.success(request, 'Deleted successfully')
        return redirect('transport_table')
    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}")
    


def update_transport_record(request,pk):
    transport_record = Transport.objects.get(id=pk)
    form = UploadTransportData(instance=transport_record)

    if request.method == 'POST':
        form = UploadTransportData(request.POST, instance=transport_record)
        if form.is_valid():
            form.save()
            return redirect('transport_table')
        
    context={'form':form,}
    return render(request,'general_data/transport_templates/update_transport_record.html',context)