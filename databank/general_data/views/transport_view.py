import datetime
from django.db import DataError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Q
import pandas as pd
from ..models import Transport, Country_meta
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
    # gender_option = [choice[1] for choice in Transport.Gender_Options]
    # age_group_options=[choice[1] for choice in Transport.Age_Group_Options]

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