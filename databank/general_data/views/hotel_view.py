import datetime
from django.db import DataError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Q
import pandas as pd
from ..models import Hotel, Country_meta
from ..forms import UploadForestDataForm,UploadHotelData
from trade_data.views import tables
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.views.decorators.http import require_POST


def is_valid_queryparam(param):
    return param !='' and param is not None


def display_hotel_table(request):

    url = reverse('population_table')
    data = Hotel.objects.all()
    country_categories = Country_meta.objects.all()
    # age_group_options=[choice[1] for choice in Hotel.Age_Group_Options]

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')

    name_of_the_hotel=request.GET.get('name_of_the_hotel')
    name_of_the_city=request.GET.get('name_of_the_city')



    country_category = request.GET.get('country_category')

    if is_valid_queryparam (date_min):
        data=data.filter(Year__gte=date_min)

    if is_valid_queryparam(date_max):
        data=data.filter(Year__lte=date_max)

    if is_valid_queryparam(name_of_the_hotel):
        data=data.filter(Q(Name_Of_The_Hotel__icontains=name_of_the_hotel)).distinct()

    if is_valid_queryparam(name_of_the_city):
        data=data.filter(Q(City__icontains=name_of_the_city)).distinct()
 





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
    return render(request, 'general_data/hotel_templates/hotel_table.html',context)

@require_POST
def delete_selected_hotel(request):
    selected_ids = request.POST.getlist('selected_items')
    if not selected_ids:
        messages.error(request, 'No items selected for deletion.')
        return redirect('hotel_table')
    try:
        Hotel.objects.filter(id__in=selected_ids).delete()
        messages.success(request, 'Selected items deleted successfully.')
    except Exception as e:
        messages.error(request, f'Error deleting items: {e}')

    return redirect('hotel_table')




def delete_hotel_record(request,item_id):
    try:
        item_to_delete = get_object_or_404(Hotel, id=item_id)
        item_to_delete.delete()
        messages.success(request, 'Deleted successfully')
        return redirect('hotel_table')
    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}")
    

    
def update_hotel_record(request,pk):
    hotel_record = Hotel.objects.get(id=pk)
    form = UploadHotelData(instance=hotel_record)

    if request.method == 'POST':
        form = UploadHotelData(request.POST, instance=hotel_record)
        if form.is_valid():
            form.save()
            return redirect('hotel_table')
        
    context={'form':form,}
    return render(request,'general_data/hotel_templates/update_hotel_record.html',context)