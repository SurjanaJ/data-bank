import datetime
from django.db import DataError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Q
import pandas as pd
from ..models import PopulationData, Country_meta
from ..forms import UploadForestDataForm,UploadPopulationData
from trade_data.views import tables
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.views.decorators.http import require_POST


def is_valid_queryparam(param):
    return param !='' and param is not None


def display_population_table(request):

    url = reverse('population_table')
    data = PopulationData.objects.all()
    country_categories = Country_meta.objects.all()
    gender_option = [choice[1] for choice in PopulationData.Gender_Options]
    age_group_options=[choice[1] for choice in PopulationData.Age_Group_Options]

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')

    country_category = request.GET.get('country_category')
    gender=request.GET.get('gender')
    age_group=request.GET.get('age_group')
    min_population = request.GET.get('minimum_area')
    max_population = request.GET.get('maximum_area')


    if is_valid_queryparam(date_min):
        data=data.filter(Year__gte=date_min)

    if is_valid_queryparam(date_max):
        data=data.filter(Year__lt=date_max)

    if is_valid_queryparam(country_category) and country_category != '--':
        data = data.filter(Country_id=country_category)
    
    if is_valid_queryparam(min_population):
        data = data.filter(Population_gte=min_population)

    if is_valid_queryparam(max_population):
        data = data.filter(Population__lt=max_population)

    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    

    context={
        'tables':tables,
        'data_len':len(data),
        'page':page,
        'query_len': len(page),
        'country_categories':country_categories,
        'gender_options':gender_option,
        'age_group_options':age_group_options
    }
    return render(request, 'general_data/population_templates/population_table.html',context)

@require_POST
def delete_selected_population(request):
    selected_ids = request.POST.getlist('selected_items')
    if not selected_ids:
        messages.error(request, 'No items selected for deletion.')
        return redirect('population_table')
    try:
        PopulationData.objects.filter(id__in=selected_ids).delete()
        messages.success(request, 'Selected items deleted successfully.')
    except Exception as e:
        messages.error(request, f'Error deleting items: {e}')

    return redirect('population_table')


def delete_population_record(request,item_id):
    try:
        item_to_delete = get_object_or_404(PopulationData, id=item_id)
        item_to_delete.delete()
        messages.success(request, 'Deleted successfully')
        return redirect('population_table')
    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}")



def update_population_record(request,pk):
    population_record = PopulationData.objects.get(id=pk)
    form = UploadPopulationData(instance=population_record)

    if request.method == 'POST':
        form = UploadPopulationData(request.POST, instance=population_record)
        if form.is_valid():
            form.save()
            return redirect('population_table')
        
    context={'form':form,}
    return render(request,'general_data/population_templates/update_population_record.html',context)




