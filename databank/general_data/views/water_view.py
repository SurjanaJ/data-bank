import datetime
from django.db import DataError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Q
import pandas as pd
from ..models import Water, Country_meta
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
    # gender_option = [choice[1] for choice in Water.Gender_Options]
    # age_group_options=[choice[1] for choice in Water.Age_Group_Options]

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')

    country_category = request.GET.get('country_category')
    gender=request.GET.get('gender')
    age_group=request.GET.get('age_group')



    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    

    context={
        'tables':tables,
        'data_len':len(data),
        'page':page,
        'country_categories':country_categories,
        # 'gender_Options':gender_option,
        # 'age_group_options':age_group_options
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