import datetime
from django.db import DataError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Q
import pandas as pd
from ..models import Water, Country_meta,Water_Meta
from ..forms import UploadForestDataForm,UploadWaterData
from trade_data.views import tables
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.views.decorators.http import require_POST


def is_valid_queryparam(param):
    return param !='' and param is not None


def display_water_table(request):

    url = reverse('water_table')
    data = Water.objects.all()
    country_categories = Country_meta.objects.all()
    water_options = Water_Meta.objects.all()
    unit_options = [choice[1] for choice in Water.Unit_Options]


    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')

    country_category = request.GET.get('country_category')
    water_code = request.GET.get('water_code')
    name_of_the_river = request.GET.get('name_of_the_river')
    unit=request.GET.get('unit')
    min_volume = request.GET.get('minimum_volume')
    max_volume = request.GET.get('maximum_volume')


    if is_valid_queryparam (date_min):
        data=data.filter(Year__gte=date_min)

    if is_valid_queryparam(date_max):
        data=data.filter(Year__lte=date_max)

    if is_valid_queryparam(country_category) and country_category != '--':
        data = data.filter(Country_id=country_category)

    if is_valid_queryparam(water_code) and water_code != '--':
        data = data.filter(Water_Type_Code_id=water_code)

    if is_valid_queryparam(unit) and unit != '--':
        data = data.filter(Unit=unit)


    if is_valid_queryparam(name_of_the_river):
        data=data.filter(Q(Name_Of_The_River__icontains=name_of_the_river)).distinct()

    if is_valid_queryparam(min_volume):
        data = data.filter(Volume__gte=min_volume)

    if is_valid_queryparam(max_volume):
        data = data.filter(Volume__lt=max_volume)

    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    

    context={
        'tables':tables,
        'data_len':len(data),
        'page':page,
        'query_len': len(page),
        'country_categories':country_categories,
        'water_options':water_options,
        'unit_options':unit_options,

    }
    return render(request, 'general_data/water_templates/water_table.html',context)

@require_POST
def delete_selected_water(request):
    selected_ids = request.POST.getlist('selected_items')
    if not selected_ids:
        messages.error(request, 'No items selected for deletion.')
        return redirect('water_table')
    try:
        Water.objects.filter(id__in=selected_ids).delete()
        messages.success(request, 'Selected items deleted successfully.')
    except Exception as e:
        messages.error(request, f'Error deleting items: {e}')

    return redirect('water_table')


def delete_water_record(request,item_id):
    try:
        item_to_delete = get_object_or_404(Water, id=item_id)
        item_to_delete.delete()
        messages.success(request, 'Deleted successfully')
        return redirect('water_table')
    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}")
    


def update_water_record(request,pk):
    water_record = Water.objects.get(id=pk)
    form = UploadWaterData(instance=water_record)

    if request.method == 'POST':
        form = UploadWaterData(request.POST, instance=water_record)
        if form.is_valid():
            form.save()
            return redirect('water_table')
        
    context={'form':form,}
    return render(request,'general_data/water_templates/update_water_record.html',context)